import test from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import {
    applyPatch,
    validateInput,
    validateManifest,
    sha256,
} from "./patcher.mjs";

const root = new URL("../", import.meta.url);
const read = async (path) =>
    new Uint8Array(await readFile(new URL(path, root)));
const manifest = JSON.parse(
    await readFile(new URL("build/web-patcher/manifest.json", root)),
);
const delta = await read(`build/web-patcher/${manifest.patch.file}`);
const original = await read("inputs/MX1_UPD.original.bin");
const candidate = await read("build/mainline/MXPLUS_MAINLINE_UNTESTED.bin");
const clone = (value) => structuredClone(value);

test("browser algorithm reproduces the sole committed candidate without mutating the input", async () => {
    const before = original.slice();
    assert.deepEqual(await applyPatch(original, delta, manifest), candidate);
    assert.deepEqual(original, before);
});

test("wrong revision, corruption, ZIP, truncation and already-patched files are rejected", async () => {
    const changed = original.slice();
    changed[0] ^= 1;
    for (const input of [
        changed,
        candidate,
        original.subarray(1),
        new Uint8Array([0x50, 0x4b]),
    ]) {
        await assert.rejects(validateInput(input), /original|size/);
    }
});

test("corrupt patch, incorrect output hash and mixed release assets cannot produce output", async () => {
    const corrupt = delta.slice();
    corrupt[corrupt.length - 10] ^= 1;
    await assert.rejects(applyPatch(original, corrupt, manifest), /integrity/);
    const mismatch = clone(manifest);
    mismatch.output.sha256 = "0".repeat(64);
    await assert.rejects(
        applyPatch(original, delta, mismatch),
        /Patched firmware/,
    );
    const mixed = clone(manifest);
    mixed.patch.sha256 = "0".repeat(64);
    mixed.patch.file = `patch-${mixed.patch.sha256}.json`;
    await assert.rejects(applyPatch(original, delta, mixed), /integrity/);
});

test("manifest cannot loosen the fixed input, experimental label or local patch path", () => {
    const mutations = [
        (m) => (m.input.sha256 = m.output.sha256),
        (m) => m.input.size++,
        (m) => m.output.size++,
        (m) => (m.status = "STABLE"),
        (m) => (m.output.filename = "MX-1_UPD.BIN"),
        (m) => (m.patch.file = "https://example.com/patch.json"),
        (m) => (m.sourceCommit = "../main"),
        (m) => (m.format = "v2"),
    ];
    for (const mutate of mutations) {
        const m = clone(manifest);
        mutate(m);
        assert.throws(() => validateManifest(m), /Invalid release/);
    }
});

test("malformed ranges, overlap, encoding, empty and unknown patch formats fail closed", async () => {
    const patches = [
        { format: "v2", runs: [] },
        { format: "mxplus-xor-v1", runs: [] },
        ...[
            [{ offset: -1, xor: "AQ==" }],
            [{ offset: 0.5, xor: "AQ==" }],
            [{ offset: original.length, xor: "AQ==" }],
            [{ offset: original.length - 1, xor: "AQID" }],
            [
                { offset: 2, xor: "AQID" },
                { offset: 4, xor: "AQ==" },
            ],
            [{ offset: 0, xor: "!!!!" }],
            [{ offset: 0, xor: "" }],
            [{ offset: 0, xor: "AR==" }], // Noncanonical base64.
            [null],
        ].map((runs) => ({ format: "mxplus-xor-v1", runs })),
    ];
    for (const patch of patches) {
        const bytes = new TextEncoder().encode(JSON.stringify(patch));
        const m = clone(manifest);
        m.patch.sha256 = await sha256(bytes);
        m.patch.file = `patch-${m.patch.sha256}.json`;
        await assert.rejects(
            applyPatch(original, bytes, m),
            /Invalid patch|beyond/,
        );
    }
});

test("published directory is an explicit allowlist with no full firmware or repository files", async () => {
    const names = await readdir(new URL("build/web-patcher/", root));
    assert.deepEqual(
        names.sort(),
        [
            ".nojekyll",
            "index.html",
            "style.css",
            "app.mjs",
            "patcher.mjs",
            "favicon.svg",
            "manifest.json",
            manifest.patch.file,
        ].sort(),
    );
    for (const name of names) {
        const bytes = await read(`build/web-patcher/${name}`);
        assert.notEqual(await sha256(bytes), manifest.input.sha256);
        assert.notEqual(await sha256(bytes), manifest.output.sha256);
    }
});
