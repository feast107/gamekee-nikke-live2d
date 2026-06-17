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
        #controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            z-index: 10;
        }
        .pose-btn {
            padding: 8px 16px;
            border: 1px solid rgba(255,255,255,0.6);
            border-radius: 20px;
            background: rgba(0,0,0,0.4);
            color: #fff;
            cursor: pointer;
            font-size: 14px;
        }
        .pose-btn.active {
            background: rgba(255,255,255,0.25);
            border-color: #fff;
        }
    </style>
</head>
<body>
    <div id="player-container"></div>
    <div id="controls">
        __BUTTONS__
    </div>

    <script src="spine-player-4.1.54.js"></script>
    <script>
        const characterData = __CHARACTER_DATA__;
        const clickAnimationMap = {
            full: "action",
            aim: "aim_fire",
            cover: "cover_reload"
        };

        let player = null;
        let animationList = [];
        let currentType = "__DEFAULT_POSE__";
        let animationTimer = null;

        function getAssetUrls(type) {
            const entry = characterData[type];
            if (!entry) return null;
            const base = entry.base;
            return {
                skelUrl: base + ".skel",
                atlasUrl: base + ".atlas",
                jsonUrl: "",
                pngUrl: base + ".png"
            };
        }

        function getViewport(type) {
            const entry = characterData[type];
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

        function loadPose(type) {
            currentType = type;
            if (player) {
                player.dispose();
                player = null;
            }
            const urls = getAssetUrls(type);
            if (!urls) return;

            const container = document.getElementById("player-container");
            player = new spine_4_1_54.SpinePlayer(container, {
                skelUrl: urls.skelUrl,
                atlasUrl: urls.atlasUrl,
                jsonUrl: urls.jsonUrl,
                pngUrl: urls.pngUrl,
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
                    console.error("Spine player failed to load", type, err);
                }
            });

            document.querySelectorAll(".pose-btn").forEach(btn => {
                btn.classList.toggle("active", btn.dataset.pose === type);
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

        document.querySelectorAll(".pose-btn").forEach(btn => {
            btn.addEventListener("click", () => loadPose(btn.dataset.pose));
        });

        loadPose(currentType);
    </script>
</body>
</html>
"""


def generate_html(
    output_path: Path,
    title: str,
    character_data: Dict[str, Any],
    default_pose: str = "full",
    background: str = "#1a1a2e",
) -> Path:
    """
    Generate a standalone HTML demo page.

    Args:
        output_path: Destination file path.
        title: Page title.
        character_data: Mapping from pose to local asset metadata.
        default_pose: Initial pose to display.
        background: CSS background value.

    Returns:
        Path to generated HTML file.
    """
    buttons = "\n        ".join(
        f'<button class="pose-btn" data-pose="{pose}">{pose.upper()}</button>'
        for pose in character_data.keys()
    )

    html = (
        HTML_TEMPLATE.replace("__TITLE__", title)
        .replace("__BACKGROUND__", background)
        .replace("__BUTTONS__", buttons)
        .replace("__CHARACTER_DATA__", json.dumps(character_data, ensure_ascii=False, indent=2))
        .replace("__DEFAULT_POSE__", default_pose)
    )

    output_path.write_text(html, encoding="utf-8")
    return output_path
