"""
Generate standalone HTML demo pages for a character.
"""

import json
from pathlib import Path
from typing import Any, Dict


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>__TITLE__</title>
    <link id="spine-css" rel="stylesheet" href="__DEFAULT_CSS__">
    <style>
        html, body {
            margin: 0; padding: 0;
            width: 100%; height: 100%;
            background: __BACKGROUND__;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
        }
        #player-container {
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        #skin-controls, #pose-controls {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            z-index: 10;
        }
        #skin-controls {
            top: 20px;
        }
        #pose-controls {
            bottom: 20px;
        }
        .skin-btn, .pose-btn, #debug-toggle {
            padding: 8px 16px;
            border: 1px solid rgba(255,255,255,0.6);
            border-radius: 20px;
            background: rgba(0,0,0,0.4);
            color: #fff;
            cursor: pointer;
            font-size: 14px;
        }
        .skin-btn.active, .pose-btn.active, #debug-toggle.active {
            background: rgba(255,255,255,0.25);
            border-color: #fff;
        }
        #debug-toggle {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 40;
        }
        #debug-panel {
            position: absolute;
            top: 0;
            right: -360px;
            width: 320px;
            height: 100vh;
            background: rgba(20, 20, 30, 0.95);
            border-left: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            z-index: 30;
            padding: 16px;
            box-sizing: border-box;
            overflow-y: auto;
            transition: right 0.25s ease;
        }
        #debug-panel.open {
            right: 0;
        }
        #debug-panel h3 {
            margin: 0 0 12px 0;
            font-size: 16px;
        }
        #debug-panel .debug-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }
        #debug-panel .debug-tab {
            flex: 1;
            padding: 6px;
            border: 1px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.1);
            color: #fff;
            cursor: pointer;
            border-radius: 6px;
            font-size: 13px;
        }
        #debug-panel .debug-tab.active {
            background: rgba(255,255,255,0.3);
        }
        #debug-panel .debug-search {
            width: 100%;
            padding: 6px 8px;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            border-radius: 6px;
            box-sizing: border-box;
        }
        #debug-panel .debug-list {
            max-height: 340px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            margin-bottom: 14px;
        }
        #debug-panel .debug-item {
            padding: 6px 8px;
            cursor: pointer;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 13px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        #debug-panel .debug-item:hover {
            background: rgba(255,255,255,0.1);
        }
        #debug-panel .debug-item.active {
            background: rgba(255,255,255,0.2);
        }
        #debug-panel .debug-section {
            display: none;
        }
        #debug-panel .debug-section.active {
            display: block;
        }
        #debug-panel .control-group {
            margin-bottom: 10px;
        }
        #debug-panel .control-group label {
            display: block;
            font-size: 12px;
            margin-bottom: 4px;
            color: rgba(255,255,255,0.7);
        }
        #debug-panel .control-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        #debug-panel input[type="number"], #debug-panel input[type="range"], #debug-panel select {
            width: 100%;
            padding: 5px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            border-radius: 4px;
            font-size: 13px;
        }
        #debug-panel input[type="range"] {
            padding: 0;
        }
        #debug-panel .range-value {
            min-width: 44px;
            text-align: right;
            font-size: 12px;
        }
        #debug-panel .debug-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }
        #debug-panel .debug-actions button {
            flex: 1;
            padding: 8px;
            border: 1px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.15);
            color: #fff;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
        }
        #debug-panel .hint {
            font-size: 11px;
            color: rgba(255,255,255,0.5);
            margin-top: 10px;
            line-height: 1.4;
        }
        /* Hide the timeline/progress bar, keep the play button */
        .spine-player-timeline {
            display: none !important;
        }
    </style>
</head>
<body>
    <div id="player-container"></div>
    <div id="skin-controls">
        __SKIN_BUTTONS__
    </div>
    <div id="pose-controls"></div>
    <button id="debug-toggle">调试面板</button>
    <div id="debug-panel">
        <h3>Spine 调试面板</h3>
        <div class="debug-tabs">
            <button class="debug-tab active" data-tab="bones">骨骼</button>
            <button class="debug-tab" data-tab="slots">插槽</button>
        </div>
        <input type="text" class="debug-search" id="debug-search" placeholder="搜索名称...">
        <div class="debug-section active" id="section-bones">
            <div class="debug-list" id="bone-list"></div>
            <div id="bone-controls" style="display:none;">
                <div class="control-group">
                    <label>位置 X</label>
                    <div class="control-row">
                        <input type="range" id="bone-x-slider" min="-500" max="500" step="1">
                        <input type="number" id="bone-x" style="width:70px;" step="1">
                    </div>
                </div>
                <div class="control-group">
                    <label>位置 Y</label>
                    <div class="control-row">
                        <input type="range" id="bone-y-slider" min="-500" max="500" step="1">
                        <input type="number" id="bone-y" style="width:70px;" step="1">
                    </div>
                </div>
                <div class="control-group">
                    <label>缩放 X</label>
                    <div class="control-row">
                        <input type="range" id="bone-scaleX-slider" min="0" max="3" step="0.05">
                        <span class="range-value" id="bone-scaleX-val">1</span>
                    </div>
                </div>
                <div class="control-group">
                    <label>缩放 Y</label>
                    <div class="control-row">
                        <input type="range" id="bone-scaleY-slider" min="0" max="3" step="0.05">
                        <span class="range-value" id="bone-scaleY-val">1</span>
                    </div>
                </div>
                <div class="control-group">
                    <label>旋转</label>
                    <div class="control-row">
                        <input type="range" id="bone-rotation-slider" min="-180" max="180" step="1">
                        <span class="range-value" id="bone-rotation-val">0</span>
                    </div>
                </div>
                <div class="debug-actions">
                    <button id="bone-reset">重置</button>
                </div>
            </div>
        </div>
        <div class="debug-section" id="section-slots">
            <div class="debug-list" id="slot-list"></div>
            <div id="slot-controls" style="display:none;">
                <div class="control-group">
                    <label>透明度 (Alpha)</label>
                    <div class="control-row">
                        <input type="range" id="slot-alpha-slider" min="0" max="1" step="0.05">
                        <span class="range-value" id="slot-alpha-val">1</span>
                    </div>
                </div>
                <div class="debug-actions">
                    <button id="slot-toggle">隐藏 / 显示</button>
                    <button id="slot-reset">重置</button>
                </div>
            </div>
        </div>
        <p class="hint">提示：修改会实时生效。若当前正在播放动画，动画关键帧可能会覆盖手动修改。</p>
    </div>

    <script src="__DEFAULT_JS__"></script>
    <script>
        const characterData = __CHARACTER_DATA__;
        const skins = characterData.skins || [characterData];
        const runtimeMap = __RUNTIME_MAP__;
        const clickAnimationMap = {
            full: "action",
            aim: "aim_fire",
            cover: "cover_reload"
        };

        let player = null;
        let animationList = [];
        let currentSkin = __DEFAULT_SKIN__;
        let currentType = "__DEFAULT_POSE__";
        let animationTimer = null;
        let loadedRuntimes = {};
        const poseOrder = ["full", "aim", "cover"];

        // Debug panel state
        let debugTab = "bones";
        let selectedBone = null;
        let selectedSlot = null;
        let ignoreInputEvent = false;

        function loadScript(url) {
            return new Promise((resolve, reject) => {
                if (loadedRuntimes[url]) return resolve();
                const script = document.createElement("script");
                script.src = url;
                script.onload = () => {
                    loadedRuntimes[url] = true;
                    resolve();
                };
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }

        function setCss(url) {
            const link = document.getElementById("spine-css");
            if (link) link.href = url;
        }

        async function ensureRuntime(version) {
            const meta = runtimeMap[version] || runtimeMap["4.1"];
            setCss(meta.css);
            await loadScript(meta.js);
            return meta.var;
        }

        function getSpineConstructor(varName) {
            const parts = varName.split(".");
            let obj = window;
            for (const part of parts) {
                obj = obj[part];
                if (!obj) return null;
            }
            return obj;
        }

        function getAssetUrls(skinIndex, type) {
            const skin = skins[skinIndex];
            const entry = skin && skin[type];
            if (!entry) return null;
            const base = entry.base;
            return {
                skelUrl: base + ".skel",
                atlasUrl: base + ".atlas",
                jsonUrl: ""
            };
        }

        function autoPlayIdle(p) {
            const animations = p.skeleton && p.skeleton.data && p.skeleton.data.animations;
            if (!animations) return;
            const idleAnim = animations.find(a => /idle/i.test(a.name));
            if (idleAnim && p.animationState) {
                p.animationState.setAnimation(0, idleAnim.name, true);
                p.play();
            }
        }

        function getAvailablePose(skin) {
            for (const p of poseOrder) {
                if (skin && skin[p]) return p;
            }
            return skin && Object.keys(skin)[0];
        }

        function renderPoseButtons(skinIndex) {
            const controls = document.getElementById("pose-controls");
            if (!controls) return;
            controls.innerHTML = "";
            const skin = skins[skinIndex];
            if (!skin) return;
            const poses = poseOrder.filter(p => skin[p]).concat(
                Object.keys(skin).filter(p => !poseOrder.includes(p))
            );
            poses.forEach(pose => {
                const btn = document.createElement("button");
                btn.className = "pose-btn" + (pose === currentType ? " active" : "");
                btn.dataset.pose = pose;
                btn.textContent = pose.toUpperCase();
                btn.addEventListener("click", () => loadPose(currentSkin, pose));
                controls.appendChild(btn);
            });
        }

        async function loadPose(skinIndex, type) {
            const skin = skins[skinIndex];
            if (!skin) return;
            if (!skin[type]) {
                type = getAvailablePose(skin);
            }
            currentSkin = skinIndex;
            currentType = type;
            if (player) {
                player.dispose();
                player = null;
            }

            const entry = skin[type];
            if (!entry) return;

            const version = entry.spine_version || "4.1";
            const spineVar = await ensureRuntime(version);
            const SpinePlayer = getSpineConstructor(spineVar);
            if (!SpinePlayer) {
                console.error("Spine runtime not found", spineVar);
                return;
            }

            const urls = getAssetUrls(skinIndex, type);
            if (!urls) return;

            const container = document.getElementById("player-container");
            player = new SpinePlayer(container, {
                skelUrl: urls.skelUrl,
                atlasUrl: urls.atlasUrl,
                jsonUrl: urls.jsonUrl,
                alpha: true,
                backgroundColor: "#00000000",
                preserveDrawingBuffer: true,
                premultipliedAlpha: true,
                success: function(loadedPlayer) {
                    window.spinePlayer = player = loadedPlayer;
                    const animData = loadedPlayer.skeleton && loadedPlayer.skeleton.data;
                    animationList = animData && animData.animations ? animData.animations.map(a => ({
                        name: a.name,
                        duration: a.duration
                    })) : [];
                    autoPlayIdle(loadedPlayer);
                    refreshDebugLists();
                },
                error: function(err) {
                    console.error("Spine player failed to load", skinIndex, type, err);
                }
            });

            document.querySelectorAll(".skin-btn").forEach(btn => {
                btn.classList.toggle("active", parseInt(btn.dataset.skin) === currentSkin);
            });
            renderPoseButtons(currentSkin);
        }

        function onPointerDown() {
            if (!player || animationTimer) return;
            const anim = clickAnimationMap[currentType];
            const animData = animationList.find(a => a.name === anim);
            if (animData && player.animationState) {
                player.animationState.setAnimation(0, anim, false);
                player.play();
                animationTimer = setTimeout(onPointerUp, 1000 * animData.duration);
            }
        }

        function onPointerUp() {
            if (animationTimer) clearTimeout(animationTimer);
            animationTimer = null;
            if (player) autoPlayIdle(player);
        }

        const container = document.getElementById("player-container");
        container.addEventListener("mousedown", onPointerDown);
        container.addEventListener("touchstart", onPointerDown, { passive: false });
        container.addEventListener("mouseup", onPointerUp);
        container.addEventListener("touchend", onPointerUp, { passive: false });
        container.addEventListener("mouseleave", onPointerUp);

        document.querySelectorAll(".skin-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const newSkin = parseInt(btn.dataset.skin);
                if (newSkin === currentSkin) return;
                loadPose(newSkin, currentType);
            });
        });

        // Debug panel logic
        const debugToggle = document.getElementById("debug-toggle");
        const debugPanel = document.getElementById("debug-panel");
        const debugSearch = document.getElementById("debug-search");

        debugToggle.addEventListener("click", () => {
            debugPanel.classList.toggle("open");
            debugToggle.classList.toggle("active", debugPanel.classList.contains("open"));
        });

        document.querySelectorAll(".debug-tab").forEach(tab => {
            tab.addEventListener("click", () => {
                document.querySelectorAll(".debug-tab").forEach(t => t.classList.remove("active"));
                document.querySelectorAll(".debug-section").forEach(s => s.classList.remove("active"));
                tab.classList.add("active");
                document.getElementById("section-" + tab.dataset.tab).classList.add("active");
                debugTab = tab.dataset.tab;
                filterDebugList();
            });
        });

        debugSearch.addEventListener("input", filterDebugList);

        function getSkeleton() {
            return player && player.skeleton;
        }

        function updateSkeleton() {
            const skeleton = getSkeleton();
            if (skeleton) {
                skeleton.updateWorldTransform();
            }
        }

        function refreshDebugLists() {
            selectedBone = null;
            selectedSlot = null;
            document.getElementById("bone-controls").style.display = "none";
            document.getElementById("slot-controls").style.display = "none";
            filterDebugList();
        }

        function filterDebugList() {
            const skeleton = getSkeleton();
            const term = (debugSearch.value || "").toLowerCase();
            const boneList = document.getElementById("bone-list");
            const slotList = document.getElementById("slot-list");
            boneList.innerHTML = "";
            slotList.innerHTML = "";
            if (!skeleton) return;

            const bones = (skeleton.bones || []).filter(b => !term || (b.data && b.data.name || b.name || "").toLowerCase().includes(term));
            bones.forEach(bone => {
                const name = bone.data && bone.data.name ? bone.data.name : (bone.name || "unnamed");
                const div = document.createElement("div");
                div.className = "debug-item" + (selectedBone === bone ? " active" : "");
                div.textContent = name;
                div.title = name;
                div.addEventListener("click", () => selectBone(bone));
                boneList.appendChild(div);
            });

            const slots = (skeleton.slots || []).filter(s => !term || (s.data && s.data.name || s.name || "").toLowerCase().includes(term));
            slots.forEach(slot => {
                const name = slot.data && slot.data.name ? slot.data.name : (slot.name || "unnamed");
                const div = document.createElement("div");
                div.className = "debug-item" + (selectedSlot === slot ? " active" : "");
                div.textContent = name;
                div.title = name;
                div.addEventListener("click", () => selectSlot(slot));
                slotList.appendChild(div);
            });
        }

        // Bone controls
        function selectBone(bone) {
            selectedBone = bone;
            document.getElementById("bone-controls").style.display = "block";
            const xInput = document.getElementById("bone-x");
            const yInput = document.getElementById("bone-y");
            const xSlider = document.getElementById("bone-x-slider");
            const ySlider = document.getElementById("bone-y-slider");
            const sxSlider = document.getElementById("bone-scaleX-slider");
            const sySlider = document.getElementById("bone-scaleY-slider");
            const rotSlider = document.getElementById("bone-rotation-slider");

            xInput.value = xSlider.value = bone.x;
            yInput.value = ySlider.value = bone.y;
            sxSlider.value = bone.scaleX;
            sySlider.value = bone.scaleY;
            rotSlider.value = bone.rotation;
            document.getElementById("bone-scaleX-val").textContent = bone.scaleX.toFixed(2);
            document.getElementById("bone-scaleY-val").textContent = bone.scaleY.toFixed(2);
            document.getElementById("bone-rotation-val").textContent = bone.rotation.toFixed(0);

            filterDebugList();
        }

        function bindBoneInput(id, prop, isSlider) {
            const el = document.getElementById(id);
            el.addEventListener("input", () => {
                if (!selectedBone) return;
                let val = parseFloat(el.value);
                if (isNaN(val)) return;
                selectedBone[prop] = val;
                updateSkeleton();
                syncBoneControl(prop, val);
            });
        }

        function syncBoneControl(prop, val) {
            const slider = document.getElementById("bone-" + prop + "-slider");
            const input = document.getElementById("bone-" + prop);
            const display = document.getElementById("bone-" + prop + "-val");
            if (slider && !slider.matches(":hover")) slider.value = val;
            if (input && !input.matches(":hover")) input.value = val;
            if (display) {
                if (prop === "rotation") display.textContent = val.toFixed(0);
                else display.textContent = val.toFixed(2);
            }
        }

        bindBoneInput("bone-x", "x", false);
        bindBoneInput("bone-x-slider", "x", true);
        bindBoneInput("bone-y", "y", false);
        bindBoneInput("bone-y-slider", "y", true);
        bindBoneInput("bone-scaleX-slider", "scaleX", true);
        bindBoneInput("bone-scaleY-slider", "scaleY", true);
        bindBoneInput("bone-rotation-slider", "rotation", true);

        document.getElementById("bone-reset").addEventListener("click", () => {
            if (!selectedBone) return;
            const data = selectedBone.data;
            if (!data) return;
            selectedBone.x = data.x || 0;
            selectedBone.y = data.y || 0;
            selectedBone.scaleX = data.scaleX || 1;
            selectedBone.scaleY = data.scaleY || 1;
            selectedBone.rotation = data.rotation || 0;
            selectBone(selectedBone);
            updateSkeleton();
        });

        // Slot controls
        function selectSlot(slot) {
            selectedSlot = slot;
            document.getElementById("slot-controls").style.display = "block";
            const alpha = slot.color ? slot.color.a : 1;
            document.getElementById("slot-alpha-slider").value = alpha;
            document.getElementById("slot-alpha-val").textContent = alpha.toFixed(2);
            filterDebugList();
        }

        document.getElementById("slot-alpha-slider").addEventListener("input", function() {
            if (!selectedSlot || !selectedSlot.color) return;
            const val = parseFloat(this.value);
            selectedSlot.color.a = val;
            document.getElementById("slot-alpha-val").textContent = val.toFixed(2);
            updateSkeleton();
        });

        document.getElementById("slot-toggle").addEventListener("click", () => {
            if (!selectedSlot || !selectedSlot.color) return;
            const isHidden = selectedSlot.color.a < 0.05;
            selectedSlot.color.a = isHidden ? 1 : 0;
            document.getElementById("slot-alpha-slider").value = selectedSlot.color.a;
            document.getElementById("slot-alpha-val").textContent = selectedSlot.color.a.toFixed(2);
            updateSkeleton();
        });

        document.getElementById("slot-reset").addEventListener("click", () => {
            if (!selectedSlot || !selectedSlot.data) return;
            const setup = selectedSlot.data.color;
            if (setup) {
                selectedSlot.color.set(setup.r, setup.g, setup.b, setup.a);
            } else {
                selectedSlot.color.a = 1;
            }
            selectSlot(selectedSlot);
            updateSkeleton();
        });

        loadPose(currentSkin, currentType);
    </script>
</body>
</html>
"""


def generate_html(
    output_path: Path,
    title: str,
    character_data: Dict[str, Any],
    runtime_map: Dict[str, Dict[str, str]],
    default_skin: int = 0,
    default_pose: str = "full",
    background: str = "#1a1a2e",
) -> Path:
    """
    Generate a standalone HTML demo page.

    Args:
        output_path: Destination file path.
        title: Page title.
        character_data: Dict with a "skins" key containing a list of pose mappings.
        runtime_map: Mapping from Spine version to {js, css, var} metadata.
        default_skin: Initial skin index to display.
        default_pose: Initial pose to display.
        background: CSS background value.

    Returns:
        Path to generated HTML file.
    """
    skins = character_data.get("skins", [character_data])
    first_skin = skins[default_skin] if skins else {}
    first_version = (first_skin.get(default_pose) or first_skin.get(next(iter(first_skin)), {})).get("spine_version", "4.1")
    default_meta = runtime_map.get(first_version, runtime_map.get("4.1", {"js": "", "css": ""}))

    skin_buttons = "\n        ".join(
        f'<button class="skin-btn" data-skin="{i}">SKIN {i + 1}</button>'
        for i in range(len(skins))
    )

    pose_buttons = ""  # pose buttons are rendered dynamically by JS

    html = (
        HTML_TEMPLATE.replace("__TITLE__", title)
        .replace("__BACKGROUND__", background)
        .replace("__DEFAULT_CSS__", default_meta["css"])
        .replace("__DEFAULT_JS__", default_meta["js"])
        .replace("__SKIN_BUTTONS__", skin_buttons)
        .replace("__POSE_BUTTONS__", pose_buttons)
        .replace("__CHARACTER_DATA__", json.dumps(character_data, ensure_ascii=False, indent=2))
        .replace("__RUNTIME_MAP__", json.dumps(runtime_map, ensure_ascii=False, indent=2))
        .replace("__DEFAULT_SKIN__", str(default_skin))
        .replace("__DEFAULT_POSE__", default_pose)
    )

    output_path.write_text(html, encoding="utf-8")
    return output_path
