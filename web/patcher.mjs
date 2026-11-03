// Shared by the browser and the exact-artifact Node tests. No dependencies.
export const INPUT_SIZE = 4194320;
export const INPUT_SHA256 =
    "26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e";
const HASH = /^[a-f0-9]{64}$/;

export async function sha256(bytes) {
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), (b) =>
        b.toString(16).padStart(2, "0"),
    ).join("");
}

export function validateManifest(m) {
    if (
        m?.format !== "mxplus-release-v1" ||
        m.status !== "UNTESTED" ||
        !/^[a-f0-9]{40}$/.test(m.sourceCommit) ||
        m.input?.size !== INPUT_SIZE ||
        m.input.sha256 !== INPUT_SHA256 ||
        m.output?.size !== INPUT_SIZE ||
        !HASH.test(m.output.sha256) ||
        m.output.sha256 === INPUT_SHA256 ||
        m.output.filename !== "MX1_UPD_mxplus.bin" ||
        !HASH.test(m.patch?.sha256) ||
        m.patch.file !== `patch-${m.patch.sha256}.json`
    ) {
        throw new Error(
            "Invalid release details. Reload the page; do not use this patch.",
        );
    }
    return m;
}

export async function validateInput(input) {
    if (!(input instanceof Uint8Array) || input.byteLength !== INPUT_SIZE) {
        throw new Error(
            "Wrong file size. Extract Roland’s v1.05 ZIP and choose MX-1_UPD.BIN.",
        );
    }
    const hash = await sha256(input);
    if (hash !== INPUT_SHA256) {
        throw new Error(
            "This is not the supported original firmware. Use an unchanged MX-1_UPD.BIN from Roland’s v1.05 download.",
        );
    }
    return hash;
}

export async function applyPatch(input, patchBytes, manifest) {
    validateManifest(manifest);
    await validateInput(input);
    if (
        !(patchBytes instanceof Uint8Array) ||
        patchBytes.length > 8 * 1024 * 1024 ||
        (await sha256(patchBytes)) !== manifest.patch.sha256
    ) {
        throw new Error(
            "Patch download failed its integrity check. Reload and try again.",
        );
    }
    const patch = JSON.parse(
        new TextDecoder("utf-8", { fatal: true }).decode(patchBytes),
    );
    if (
        patch?.format !== "mxplus-xor-v1" ||
        !Array.isArray(patch.runs) ||
        patch.runs.length === 0 ||
        patch.runs.length > 100000
    ) {
        throw new Error("Invalid patch format.");
    }
    const output = input.slice();
    let end = 0;
    for (const run of patch.runs) {
        if (
            !Number.isSafeInteger(run?.offset) ||
            run.offset < end ||
            run.offset >= output.length ||
            typeof run.xor !== "string" ||
            run.xor.length === 0 ||
            run.xor.length > 4 * Math.ceil(output.length / 3) ||
            run.xor.length % 4 !== 0 ||
            /[^A-Za-z0-9+/=]/.test(run.xor)
        ) {
            throw new Error("Invalid patch range or encoding.");
        }
        const delta = atob(run.xor);
        if (btoa(delta) !== run.xor) throw new Error("Invalid patch encoding.");
        end = run.offset + delta.length;
        if (end > output.length)
            throw new Error("Patch extends beyond the firmware.");
        for (let i = 0; i < delta.length; i++)
            output[run.offset + i] ^= delta.charCodeAt(i);
    }
    if ((await sha256(output)) !== manifest.output.sha256) {
        throw new Error(
            "Patched firmware failed its SHA-256 check. No download was created.",
        );
    }
    return output;
}
