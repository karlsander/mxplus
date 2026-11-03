import {
    INPUT_SIZE,
    validateManifest,
    validateInput,
    applyPatch,
} from "./patcher.mjs";

const $ = (id) => document.getElementById(id);
const fileInput = $("firmware");
const zone = $("dropzone");
const status = $("status");
const patchButton = $("patch");
let manifest;
let selected;
let generation = 0;
let urls = [];

function report(message, kind = "") {
    status.textContent = message;
    status.dataset.kind = kind;
}

function clearResult() {
    for (const url of urls) URL.revokeObjectURL(url);
    urls = [];
    $("result").hidden = true;
    for (const id of ["download", "receipt"]) $(id).removeAttribute("href");
}

function downloadLink(id, bytes, name, type) {
    const url = URL.createObjectURL(new Blob([bytes], { type }));
    urls.push(url);
    $(id).href = url;
    $(id).download = name;
}

async function choose(file) {
    const current = ++generation;
    selected = undefined;
    patchButton.disabled = true;
    clearResult();
    if (!file) {
        report("Choose the extracted .BIN file to begin.");
        return;
    }
    if (!manifest) {
        report("Release details are unavailable. Reload the page.", "error");
        return;
    }
    if (file.size !== INPUT_SIZE) {
        report(
            "Wrong file size. Choose the extracted MX-1_UPD.BIN, not the ZIP archive.",
            "error",
        );
        return;
    }
    report("Checking the original firmware…");
    try {
        const input = new Uint8Array(await file.arrayBuffer());
        await validateInput(input);
        if (current !== generation) return;
        selected = input;
        patchButton.disabled = false;
        report(
            "Original v1.05 verified. Ready to create your patched file.",
            "success",
        );
    } catch (error) {
        if (current === generation) report(error.message, "error");
    }
}

fileInput.addEventListener("change", () => choose(fileInput.files[0]));
for (const event of ["dragenter", "dragover"])
    zone.addEventListener(event, (e) => {
        e.preventDefault();
        zone.classList.add("dragging");
    });
for (const event of ["dragleave", "drop"])
    zone.addEventListener(event, (e) => {
        e.preventDefault();
        zone.classList.remove("dragging");
    });
zone.addEventListener("drop", (e) => {
    fileInput.value = "";
    if (e.dataTransfer.files.length !== 1) {
        choose(undefined);
        report("Choose one firmware file at a time.", "error");
        return;
    }
    fileInput.files = e.dataTransfer.files;
    choose(e.dataTransfer.files[0]);
});

patchButton.addEventListener("click", async () => {
    if (!selected || !manifest) return;
    const current = ++generation;
    const input = selected;
    patchButton.disabled = true;
    clearResult();
    report("Creating and verifying the patched firmware…");
    try {
        const response = await fetch(`./${manifest.patch.file}`, {
            cache: "no-store",
        });
        if (!response.ok)
            throw new Error(
                "Could not download the patch. Reload and try again.",
            );
        const output = await applyPatch(
            input,
            new Uint8Array(await response.arrayBuffer()),
            manifest,
        );
        if (current !== generation) return;
        downloadLink(
            "download",
            output,
            manifest.output.filename,
            "application/octet-stream",
        );
        const receipt = {
            status: manifest.status,
            sourceCommit: manifest.sourceCommit,
            filename: manifest.output.filename,
            installationFilename: "MX-1_UPD.BIN",
            inputSHA256: manifest.input.sha256,
            outputSHA256: manifest.output.sha256,
            size: output.length,
            hardwareValidated: false,
        };
        downloadLink(
            "receipt",
            JSON.stringify(receipt, null, 2) + "\n",
            "MXPLUS_MAINLINE_UNTESTED-receipt.json",
            "application/json",
        );
        $("result").hidden = false;
        report(
            "Patched file verified. Download it and keep its receipt.",
            "success",
        );
        $("download").focus();
    } catch (error) {
        if (current === generation) report(error.message, "error");
    } finally {
        if (current === generation) patchButton.disabled = !selected;
    }
});

async function load() {
    try {
        if (!globalThis.crypto?.subtle)
            throw new Error("Open this page over HTTPS in a current browser.");
        const response = await fetch("./manifest.json", { cache: "no-store" });
        if (!response.ok)
            throw new Error(
                "Release details could not be loaded. Reload and try again.",
            );
        manifest = validateManifest(await response.json());
        $("candidate-hash").textContent = manifest.output.sha256;
        $("build-id").textContent = manifest.output.sha256.slice(0, 8);
        $("source").textContent =
            `Source ${manifest.sourceCommit.slice(0, 7)}`;
        $("source").href =
            `https://github.com/karlsander/mxplus/tree/${manifest.sourceCommit}`;
        fileInput.disabled = false;
        report("Choose the extracted .BIN file to begin.");
    } catch (error) {
        report(error.message, "error");
    }
}
load();
