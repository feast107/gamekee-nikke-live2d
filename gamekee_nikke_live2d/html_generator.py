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
    <link rel="stylesheet" href="spine-player-4.1.54.css">
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
        .skin-btn, .pose-btn {
            padding: 8px 16px;
            border: 1px solid rgba(255,255,255,0.6);
            border-radius: 20px;
            background: rgba(0,0,0,0.4);
            color: #fff;
            cursor: pointer;
            font-size: 14px;
        }
        .skin-btn.active, .pose-btn.active {
            background: rgba(255,255,255,0.25);
            border-color: #fff;
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
    <div id="pose-controls">
        __POSE_BUTTONS__
    </div>

    <script src="spine-player-4.1.54.js"></script>
    <script>
        const characterData = __CHARACTER_DATA__;
        const skins = characterData.skins || [characterData];
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

        function getViewport(skinIndex, type) {
            const skin = skins[skinIndex];
            const entry = skin && skin[type];
            const pos = entry && entry.position;
            const pc = pos && pos.pc && pos.pc.large;
            if (pc && pc.width && pc.height) {
                return { x: pc.x, y: pc.y, width: pc.width, height: pc.height };
            }
            const container = document.getElementById("player-container");
            return { x: 0, y: 0, width: container.clientWidth, height: container.clientHeight };
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

        function loadPose(skinIndex, type) {
            currentSkin = skinIndex;
            currentType = type;
            if (player) {
                player.dispose();
                player = null;
            }
            const urls = getAssetUrls(skinIndex, type);
            if (!urls) return;

            const container = document.getElementById("player-container");
            player = new spine_4_1_54.SpinePlayer(container, {
                skelUrl: urls.skelUrl,
                atlasUrl: urls.atlasUrl,
                jsonUrl: urls.jsonUrl,
                alpha: true,
                backgroundColor: "#00000000",
                preserveDrawingBuffer: true,
                premultipliedAlpha: true,
                success: function(loadedPlayer) {
                    const animData = loadedPlayer.skeleton && loadedPlayer.skeleton.data;
                    animationList = animData && animData.animations ? animData.animations.map(a => ({
                        name: a.name,
                        duration: a.duration
                    })) : [];
                    autoPlayIdle(loadedPlayer);
                },
                error: function(err) {
                    console.error("Spine player failed to load", skinIndex, type, err);
                }
            });

            document.querySelectorAll(".skin-btn").forEach(btn => {
                btn.classList.toggle("active", parseInt(btn.dataset.skin) === currentSkin);
            });
            document.querySelectorAll(".pose-btn").forEach(btn => {
                btn.classList.toggle("active", btn.dataset.pose === currentType);
            });
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

        document.querySelectorAll(".pose-btn").forEach(btn => {
            btn.addEventListener("click", () => loadPose(currentSkin, btn.dataset.pose));
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
    default_skin: int = 0,
    default_pose: str = "full",
    background: str = "#1a1a2e",
) -> Path:
    """
    Generate a standalone HTML demo page.

    Args:
        output_path: Destination file path.
        title: Page title.
        character_data: Either a mapping from pose to metadata, or a dict with
            a "skins" key containing a list of pose mappings.
        default_skin: Initial skin index to display.
        default_pose: Initial pose to display.
        background: CSS background value.

    Returns:
        Path to generated HTML file.
    """
    skins = character_data.get("skins", [character_data])
    first_skin = skins[default_skin] if skins else {}

    skin_buttons = "\n        ".join(
        f'<button class="skin-btn" data-skin="{i}">SKIN {i + 1}</button>'
        for i in range(len(skins))
    )

    pose_buttons = "\n        ".join(
        f'<button class="pose-btn" data-pose="{pose}">{pose.upper()}</button>'
        for pose in first_skin.keys()
    )

    html = (
        HTML_TEMPLATE.replace("__TITLE__", title)
        .replace("__BACKGROUND__", background)
        .replace("__SKIN_BUTTONS__", skin_buttons)
        .replace("__POSE_BUTTONS__", pose_buttons)
        .replace("__CHARACTER_DATA__", json.dumps(character_data, ensure_ascii=False, indent=2))
        .replace("__DEFAULT_SKIN__", str(default_skin))
        .replace("__DEFAULT_POSE__", default_pose)
    )

    output_path.write_text(html, encoding="utf-8")
    return output_path
