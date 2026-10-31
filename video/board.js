// 棋盘回放的画法。数据来自 arena/export.py：每条蛇每回合的蛇头位置和可见长度。
// drawBoard(ctx, game, turn, opt) 只依赖 turn，所以任意时间点都能直接画出来（可 seek）。
(function () {
  const SHADE = (hex, k) => {
    const n = parseInt(hex.slice(1), 16);
    let r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    r = Math.max(0, Math.min(255, Math.round(r * k)));
    g = Math.max(0, Math.min(255, Math.round(g * k)));
    b = Math.max(0, Math.min(255, Math.round(b * k)));
    return `rgb(${r},${g},${b})`;
  };
  // 8×8 的像素食物（樱桃）
  const FOOD = ["...gg...", "..g.....", ".rr.rr..", "rwrrwrr.", "rrrrrrr.", "rrrrrrr.", ".rr.rr..", "........"];
  const FOODC = { g: "#5fd35a", r: "#ff4a5a", w: "#ffd6dc" };

  function foodAt(game, turn) {
    let cur = game.food[0][1];
    for (const [t, list] of game.food) {
      if (t <= turn) cur = list; else break;
    }
    return cur;
  }

  function body(game, i, turn) {
    const H = game.heads[i];
    const t = Math.min(turn, H.length - 1);
    const k = game.vis[i][t];
    const out = [];
    for (let j = 0; j < k; j++) out.push(H[Math.max(0, t - j)]);
    return out;
  }

  function drawFood(ctx, x, y, c) {
    const u = c / 8;
    for (let r = 0; r < 8; r++) for (let q = 0; q < 8; q++) {
      const ch = FOOD[r][q];
      if (ch === ".") continue;
      ctx.fillStyle = FOODC[ch];
      ctx.fillRect(Math.round(x + q * u), Math.round(y + r * u), Math.ceil(u), Math.ceil(u));
    }
  }

  function drawSnake(ctx, segs, color, c, ox, oy, alpha, dirHint) {
    if (!segs.length) return;
    ctx.globalAlpha = alpha;
    const pad = Math.max(2, Math.round(c * 0.1));
    const dark = SHADE(color, 0.62), light = SHADE(color, 1.18);
    // 连接段：相邻两格之间补一块，让身体连成一条
    ctx.fillStyle = color;
    for (let j = 1; j < segs.length; j++) {
      const [ax, ay] = segs[j - 1], [bx, by] = segs[j];
      if (Math.abs(ax - bx) + Math.abs(ay - by) !== 1) continue;
      const x0 = Math.min(ax, bx), y0 = Math.min(ay, by);
      if (ax !== bx) ctx.fillRect(ox + x0 * c + c - pad, oy + y0 * c + pad, pad * 2, c - pad * 2);
      else ctx.fillRect(ox + x0 * c + pad, oy + y0 * c + c - pad, c - pad * 2, pad * 2);
    }
    for (let j = segs.length - 1; j >= 0; j--) {
      const [x, y] = segs[j];
      const px = ox + x * c, py = oy + y * c;
      ctx.fillStyle = dark;
      ctx.fillRect(px + pad, py + pad, c - pad * 2, c - pad * 2);
      ctx.fillStyle = j === 0 ? light : color;
      ctx.fillRect(px + pad, py + pad, c - pad * 2, c - pad * 2 - Math.max(2, Math.round(c * 0.12)));
    }
    // 眼睛
    const [hx, hy] = segs[0];
    let dx = 0, dy = -1;
    if (segs.length > 1 && (segs[1][0] !== hx || segs[1][1] !== hy)) { dx = hx - segs[1][0]; dy = hy - segs[1][1]; }
    else if (dirHint) { dx = dirHint[0]; dy = dirHint[1]; }
    const e = Math.max(3, Math.round(c * 0.22)), p = Math.max(2, Math.round(e * 0.55));
    const cx = ox + hx * c + c / 2, cy = oy + hy * c + c / 2;
    const side = [dy, -dx];
    for (const s of [-1, 1]) {
      const exx = cx + dx * c * 0.12 + side[0] * s * c * 0.2 - e / 2;
      const eyy = cy + dy * c * 0.12 + side[1] * s * c * 0.2 - e / 2;
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(Math.round(exx), Math.round(eyy), e, e);
      ctx.fillStyle = "#14141c";
      ctx.fillRect(Math.round(exx + (e - p) / 2 + dx * (e - p) / 2), Math.round(eyy + (e - p) / 2 + dy * (e - p) / 2), p, p);
    }
    ctx.globalAlpha = 1;
  }

  // opt: {cell, ox, oy, colors[], focus(可选 seat 数组：其余变暗), flash}
  window.drawBoard = function (ctx, game, turnF, opt) {
    const c = opt.cell, W = game.w, ox = opt.ox || 0, oy = opt.oy || 0;
    const turn = Math.max(0, Math.min(game.turns, Math.floor(turnF)));
    // 地面
    ctx.fillStyle = "#0e1628";
    ctx.fillRect(ox - c * 0.5, oy - c * 0.5, W * c + c, W * c + c);
    ctx.fillStyle = "#3a4a6b";
    ctx.fillRect(ox - c * 0.5, oy - c * 0.5, W * c + c, c * 0.5);
    ctx.fillRect(ox - c * 0.5, oy + W * c, W * c + c, c * 0.5);
    ctx.fillRect(ox - c * 0.5, oy, c * 0.5, W * c);
    ctx.fillRect(ox + W * c, oy, c * 0.5, W * c);
    for (let y = 0; y < W; y++) for (let x = 0; x < W; x++) {
      ctx.fillStyle = (x + y) % 2 ? "#121c31" : "#152038";
      ctx.fillRect(ox + x * c, oy + y * c, c, c);
    }
    for (const [fx, fy] of foodAt(game, turn)) drawFood(ctx, ox + fx * c + c * 0.1, oy + fy * c + c * 0.1, c * 0.8);
    const n = game.heads.length;
    for (let i = 0; i < n; i++) {
      const d = game.death[i];
      const color = opt.colors[i];
      const dim = opt.focus && !opt.focus.includes(i);
      if (d !== null && turn >= d) {
        // 刚死的几回合：灰色残影闪一下
        const since = turnF - d;
        if (since < 6) {
          const segs = body(game, i, d - 1);
          const blink = Math.floor(since * 2) % 2 === 0;
          drawSnake(ctx, segs, blink ? "#ffffff" : "#6b7280", c, ox, oy, (dim ? 0.25 : 1) * (1 - since / 6));
          const [hx, hy] = game.heads[i][d];
          const X = ox + Math.max(-0.5, Math.min(W - 0.5, hx)) * c, Y = oy + Math.max(-0.5, Math.min(W - 0.5, hy)) * c;
          ctx.strokeStyle = "#ff3b3b";
          ctx.lineWidth = Math.max(3, c * 0.16);
          ctx.globalAlpha = 1 - since / 6;
          ctx.beginPath(); ctx.moveTo(X + c * 0.15, Y + c * 0.15); ctx.lineTo(X + c * 0.85, Y + c * 0.85);
          ctx.moveTo(X + c * 0.85, Y + c * 0.15); ctx.lineTo(X + c * 0.15, Y + c * 0.85); ctx.stroke();
          ctx.globalAlpha = 1;
        }
        continue;
      }
      drawSnake(ctx, body(game, i, turn), color, c, ox, oy, dim ? 0.25 : 1);
    }
  };

  // 高亮圈：opt.ring = [座位, 起始回合, 结束回合]，在这段回合里给它的蛇头套一个闪动的黄框
  function drawRing(ctx, game, turnF, opt) {
    if (!opt.ring) return;
    const [i, a, b] = opt.ring;
    if (turnF < a || turnF > b) return;
    const H = game.heads[i];
    const t = Math.min(Math.floor(turnF), H.length - 1);
    const [hx, hy] = H[t];
    const c = opt.cell, ox = opt.ox || 0, oy = opt.oy || 0;
    const pulse = 0.5 + 0.5 * Math.sin(turnF * 3.2);
    const r = c * (1.6 + 0.4 * pulse);
    ctx.strokeStyle = "#ffd23f";
    ctx.lineWidth = Math.max(4, c * 0.22);
    ctx.strokeRect(ox + hx * c + c / 2 - r, oy + hy * c + c / 2 - r, r * 2, r * 2);
  }
  window.drawBoardRing = drawRing;
  window.drawSnakeBody = drawSnake;

  window.boardAlive = function (game, turn) {
    return game.death.map((d) => d === null || turn < d);
  };
  window.boardLen = function (game, i, turn) {
    const L = game.len[i];
    return L[Math.min(Math.floor(turn), L.length - 1)];
  };
  window.boardHp = function (game, i, turn) {
    const L = game.hp[i];
    return L[Math.min(Math.floor(turn), L.length - 1)];
  };
})();
