Let me think about this carefully. I need to write a strong Battlesnake-style bot in Python.

Key rules recap:
- Grid with walls. Moves simultaneous. Tail retracts first, so you can move into a tail cell (unless that snake just ate — tail won't move). Wait: "刚吃过食物的蛇尾巴不动" — if a snake just ate, its tail doesn't move next turn. From state, we can detect: body last two segments overlap means just ate (tail won't move next turn).
- U-turn invalid: continues in previous direction. So I must avoid moving into my neck; if I do, the actual move is previous direction.
- Health decreases 1 per turn, start 100, eat food → 100, grow by 1 (tail stays next turn).
- Head-on collisions: longest survives; tie → both die.
- Death: out of bounds, health 0, hitting any body (excluding heads — heads colliding is separate rule). Hitting another snake's head cell: that's "two heads in same cell" rule → longest survives.
- Dead snakes disappear immediately.
- Food count = num_snakes+1, respawns randomly when eaten.
- Ranking: survive longest first, then length. So survival is priority #1.

Key tactical points:
1. Never die if avoidable.
2. Avoid head-on-head with equal/longer snakes; can win head-ons vs shorter snakes (risky, since they may move away — but if both heads enter same cell, longest survives).
3. Risky cells: cells adjacent to a longer-or-equal snake's head (they might move there too → head-on). If a snake is longer than me and could move into the cell I want, that's a 50/50 death risk. Prefer avoiding.
4. Food: eat to keep health up, grow for ranking. But not at the cost of death.
5. Endgame: if I'm clearly going to survive to the end (turn limit), length matters. Also in 1v1 last-snake-standing wins immediately.

Strategy: 
- Compute for each of my 3 possible moves (excluding neck-reverse) a safety score:
  - Immediate collision (wall, body cells occupied after tail retraction, heads).
  - Flood fill space after move (accounting for tails retracting).
  - Head-on risk with bigger/equal snakes.
  - Distance to nearest food, health considerations.
  - Voronoi territory? In 31x31 with 11 snakes, flood fill + food is probably fine.

Time budget: 50ms per turn. Python. Should be careful. A flood fill on 31x31 = 961 cells, per move × 3 moves = fine. Even multiple flood fills OK.

Let me design the decision function:

1. Parse state. My head, neck, body, length, health.
2. Compute occupancy after this turn's movement: cells occupied by snake bodies. For each snake, tail cell is free UNLESS the snake will grow this turn (i.e., its last two body segments are equal → it just ate, tail stays). Actually careful: tail retracts at move; if snake eats this turn, tail stays. But eating this turn depends on where its head goes. Hmm, rule: "移动：每条蛇的头朝选定方向走一格，尾巴同时缩回一格" — tail always retracts during movement. Then "吃食物：...身体长 1 节（新的一节加在尾巴上，所以吃到后的下一回合尾巴不动）". So growth adds a segment at the tail position, meaning the tail cell stays occupied next turn. So: this turn, tail cell is free unless the snake's body has last two segments overlapping (it just ate last turn, tail stays this turn).

   So occupancy for this turn: body[0..len-2], plus body[len-1] if body[-1]==body[-2] (just ate). Also heads of other snakes: their heads will move, so head cells will be vacated... but heads could stay? No — every snake must move each turn (they give a direction; if invalid U-turn, they continue in previous direction — they still move). So heads move. But where they move is unknown. Head cell itself becomes neck this turn. So after movement, old head cell is occupied (as neck). Actually old head cell = new body's second segment, occupied. So all body cells except possibly the tail remain occupied. Tail cell free unless just-ate.

3. For each of my candidate moves (dir ≠ reverse of neck; if neck == head (stacked start), all 4 allowed):
   - newHead = head + dir.
   - Check wall: in bounds.
   - Check body collision: newHead not in occupied set (computed above). Note: my own tail retracts too (unless I just ate — detect from my body last two).
   - Head-on: for each other alive snake, if newHead is adjacent to their head and their length >= my length (after my growth? lengths compare at collision: "最长的那条活下来" — lengths at time of collision; if I eat this turn I grow by 1 this turn... eating adds segment at tail, so my length becomes len+1? Actually growth: "身体长 1 节（新的一节加在尾巴上，所以吃到后的下一回合尾巴不动）" — length +1 immediately upon eating. So if I move onto food and the other snake's head enters same cell, my length is my current length +1? Hmm, the order: move, hunger, eat, then elimination. So eating happens before elimination, so my length includes the growth. Similarly the other snake. Let me compute effective length: len + 1 if the snake's head lands on food.
     - If other snake length_effective > mine: their head could move into newHead → I die. This is a "risky" cell. If equal: both die. If mine bigger: they die, I survive (and eat their... no, dead snakes disappear, no food). Actually if they die and I survive, fine.
   - Risk quantification: risky_moves where a bigger-or-equal snake could also move. How much to avoid? Strong bots avoid. But sometimes the other snake has only that one safe move, etc. Simple approach: strongly penalize but not absolutely forbid if health critical.
   
4. Space evaluation: flood fill from newHead on the post-move board (my body shifted: head added, tail removed unless eating). Approximate other snakes as static (their bodies after their tail retraction). Count reachable cells. Also flood-fill quality: prefer more space; if space < some threshold (like < my length or small), heavy penalty.

   Better: flood fill with my new body. To do it properly: my new body = [newHead] + my old body[:-1] (or +old body if eating... if I eat, tail stays: new body = [newHead] + old_body). Hmm: eating adds segment at tail so total length +1: new body = [newHead] + old body (all of it). If not eating: [newHead] + old body[:-1].

   For flood fill, treat my body as wall, other snakes' bodies as walls (with tails retracted). Reachable area count.

5. Food: choose target food considering distance and contention. Prefer food I can reach before others, and consider health. If health low (< ~30?), prioritize eating aggressively. Also prefer food far from other snakes' heads (less contested).

6. Decision: among safe moves (no immediate death, adequate space), pick the one minimizing distance to target food, with adjustments:
   - Penalize head-on risk heavily.
   - Penalize small flood-fill space.
   - Avoid moving into cells adjacent to bigger snakes' heads even if not the same cell (they could cut us off)? Flood fill handles some of that.

7. Endgame/timing: if health is fine and there's a lot of game left, growth matters for ranking among survivors. But survival first. Actually ranking: survive longer first; among survivors compare length at end. In FFA with 11 snakes over 800 turns, likely snakes die. In 1v1 500 turns, possibly both survive to limit → then length decides. So in 1v1, eating matters a lot when safe (it's zero-sum-ish: food I eat is food they don't get).

1v1 specific: If I can trap the opponent (cut off their space), great, but that's advanced. Keep it simpler but solid.

Also important: wall-hug / tail-chase behavior when no food needed? If health high, still need food eventually since health decays. Average time to food matters. Keep eating whenever safe is generally good — growth also helps win head-ons and ranking.

Let me think about the health management: health 100, lose 1/turn. Need food roughly every ~90 turns. In 31x31 with 12 food, plenty. In 15x15 with 3 food, fine.

Danger: chasing food into contested areas. Weight food choice: prefer food where my distance < opponents' distance (closest snake distance), or where I have health advantage.

Let me now think about flood fill details more carefully, and about "just ate" detection:

body[-1] == body[-2] means tail won't move this turn. In the example, snake 1 body [[9,3],[9,4],[9,5],[9,5]] — yes last two overlap.

But note: at game start, all 3 segments stacked: body = [[x,y],[x,y],[x,y]]. Then neck == head, so U-turn rule: what's "原方向"? At turn 1, there is no previous direction. The rule says U-turn (moving back to neck cell) is invalid, continue previous direction. With neck == head, any move goes to a cell ≠ neck... wait neck cell == head cell, so moving anywhere is not "走回自己脖子那一格"? Moving to the neck cell would mean staying put, impossible since moves always move one cell. Hmm, actually if body is [[x,y],[x,y],[x,y]], neck = (x,y) = head. Any direction moves to a new cell ≠ neck. So all 4 moves valid at turn 1? Probably. Also if body[-1]==body[-2] (all stacked), tail won't move. So occupancy at start = just the single cell.

Also, what's the "previous direction" for U-turn detection? I need to track my previous direction — I can compute from head and neck: neck = body[1]; previous direction = head - neck. If neck == head, no restriction.

Edge: When I would return an invalid U-turn, the engine moves me in previous direction instead — dangerous because that might be into a wall. So never return U-turn.

Also the timeout fallback: 3 consecutive bad turns → straight forever → death. So keep code fast and exception-safe. Wrap everything in try/except and have a safe fallback: return any move that doesn't immediately kill, else straight. Actually if exception occurs, judge uses "原方向直行" — previous direction. I should compute previous direction and make the fallback: try to return a safe move; if all else fails, return something valid.

Let me structure:

```python
import random  # already seeded

DIRS = {"up": (0,-1), "down": (0,1), "left": (-1,0), "right": (1,0)}
```

Global: prev_dir (my last chosen direction) to handle... actually not needed since we can compute from body.

decide(state):
  try:
    return _decide(state)
  except Exception:
    # fallback: pick any non-immediately-fatal move
    try: return _fallback(state)
    except: return "up"

Now _decide:

Parse:
```
w = state["width"]; h = state["height"]
me = find snake with id == you
my_head = tuple(me["body"][0])
my_neck = tuple(me["body"][1]) if len>1 else my_head
my_body = [tuple(p) for p in me["body"]]
my_len = me["length"]  # == len(body)? maybe; use len(body)
my_health = me["health"]
food = set of tuples
snakes = others alive
```

Occupied cells for this turn (cells that will be blocked after everyone moves):
For each snake s (including me):
  body = s.body
  occupied.add(body[i]) for i in 0..len-2
  if body[-1] == body[-2]: occupied.add(body[-1])  # tail stays
Note: heads move away but their old head cell remains (it's within 0..len-2). Good.

Wait, subtle: a snake's head could move onto its own tail cell (fine). Our occupancy is approximation of "after all move" — actually cells that kill me are: any snake body cell after movement. After movement, snake s occupies: new_head, body[0..len-2] (old head becomes 2nd segment...), hmm let me recompute: after move, body = [new_head] + old_body[0:len-1] if not eating, or [new_head] + old_body if eating. Either way, old body[0..len-2] are occupied, tail cell (old body[-1]) is occupied only if eating. So occupied-by-s = old_body[0..len-2] + (tail if eating). Eating depends on new_head on food. Unknown for others. Conservative: include other snake's tail always? That's over-conservative (can't follow tails). The prompt explicitly notes "可以跟着别人的尾巴走" as a feature. For other snakes, tail is free unless they just ate (detectable from body[-1]==body[-2]) OR they eat this turn (head lands on food — possible if food adjacent to their head). Hmm.

To be safe but practical: treat other snake's tail as blocked if (they just ate) or (a food is adjacent to their head and they might move onto it... which they might not). Simpler: treat other tail as free unless just-ate. Risk: they eat this turn, tail stays, and I move into tail cell → I die. Probability they move onto adjacent food is maybe 50%+. In high-stakes (avoiding death), accepting some risk is needed. Weight: moving onto a cell that is another's tail-when-they-might-eat: risky but not fatal-level. I'll mark such cells as "uncertain" — allow but slightly penalized, and forbid if health critical? Actually simpler: treat those cells as blocked when computing the "safe" set, but if no safe move exists, allow them (fallback levels).

Hmm, let me keep it manageable: 

blocked_strong = old bodies 0..len-2 for all snakes + tails of just-ate snakes.
tail_uncertain = tails of other snakes that have food adjacent to their head (they might eat this turn and tail stays). Actually also MY tail if I might eat — but I know my own move, so for my own move evaluation I can compute exactly.

For my move evaluation:
- candidate cells = 4 neighbors, excluding neck-reverse (or neck if neck==head: all valid? neck==head means... at spawn, moving anywhere is not into neck since neck cell == head cell — moving to any adjacent cell is fine. Wait, moving into the neck cell: neck cell is head's cell itself; you can't move to your own cell. So all 4 valid).

Actually wait — one more subtlety about U-turn: "掉头（走回自己脖子那一格）无效" — neck is body[1]. If body[1] == body[0] (stacked spawn), no cell is "the neck cell" distinct from head... any move goes to a different cell. So all 4 fine.

For each candidate move:
1. In bounds.
2. newHead not in blocked_strong (where blocked_strong includes my own body cells except my tail — with my tail handling: my tail retracts unless I eat this turn; I know if newHead is food. So compute per-candidate: cells that kill me = for each snake: body[0..len-2], plus body[-1] if (that snake just ate) or (snake == me and I'm eating this turn) or (snake != me and they might eat — uncertain). Let me include other snakes' tails in blocked if they could eat (food adjacent to their head and that food cell is reachable by them, i.e., the food cell != ... whatever). Simplify: other tail blocked if (just ate) or (∃ food adjacent to their head). Hmm, that could be common in FFA with 12 foods. That reduces "follow tail" opportunities. Trade-off. Deaths from this are rare-ish but fatal. Let me be precise: other snake's tail stays iff their head moves onto food this turn. Their head must be adjacent to that food. If no food adjacent to their head → tail definitely moves → free. If food adjacent → maybe. I'll treat as blocked for safety scoring but allow at lower tier if necessary. Actually, alternatively: treat as risky with a penalty, similar to head-on risk. Let me create a tiered system:

Tier 0 (fatal for sure): wall, body[0..len-2] of any snake, tail of just-ate snake, my own tail if I eat (I know this — if newHead on food and my body[-1] != my body[-2], my tail retracts... wait no: if I eat, my tail does NOT retract? Let me re-read: "移动：...尾巴同时缩回一格" — tail retracts every move. "吃食物：...身体长 1 节（新的一节加在尾巴上，所以吃到后的下一回合尾巴不动）" — the new segment is added at the tail, i.e., at the cell the tail just left... so effectively tail stays. Net: when eating, length +1 and tail cell remains occupied THIS turn? "吃到后的下一回合尾巴不动" — the NEXT turn tail doesn't move. So this turn (the turn of eating): tail retracted normally, then new segment added at... "加在尾巴上" — appended at the tail. The example given: body [..., [9,5],[9,5]] means after eating, the last two segments overlap. So after eating, tail cell = the cell where tail was before retraction? Let's verify with the example: they say last two overlapping means "它刚吃到食物，下一回合尾巴不动". So post-eat state has duplicated tail. So when I eat this turn: my body becomes [new_head] + old_body entirely (length+1), with tail cell = old tail cell... hmm: old body [H, b1, b2, T]. Move: head→newH, tail T retracts: [newH, H, b1, b2]. Eat: add segment at tail: [newH, H, b1, b2, b2]? or [newH,H,b1,b2,T]? "新的一节加在尾巴上" and next turn tail doesn't move → the final two cells overlap: [newH, H, b1, b2, b2]. So tail cell (b2's position... old T retracted, new tail = b2 duplicated). So after eating, occupied cells include old tail position? The old tail T is now free (retracted during move). The new duplicate is at old body[-2]. Hmm wait: [H,b1,b2,T] length 4. After move+eat: [newH, H, b1, b2, b2] length 5. The cell T is vacated. Cell b2 occupied twice. Next turn, tail (the second b2) doesn't move: after moving, [newH2, newH, H, b1, b2] — tail stays at b2.

So for MY candidate move onto food: my new body = [newHead] + old_body (all of it, len+1). Cells killing me = my old body[0..len-2]... wait but old body[-1] (tail T) — in new body, cells are newHead, old[0..len-1]. So old tail cell IS occupied after I eat? New body includes old T as its last element? [newH, H, b1, b2, b2] — old body was [H,b1,b2,T]; new body = [newH,H,b1,b2,b2]. The last element is b2 duplicated, NOT T. So T is free. Occupied after I eat: newHead,H,b1,b2. Same as old body[0..len-2] plus newHead. And old tail T is free regardless!

Wait, so when does "tail doesn't move" matter? The NEXT turn: body [..., b2, b2]; when moving, tail (second b2) stays: occupied = body[0..len-2] + body[-1] where body[-1]==body[-2]. So: the tail-stays condition is visible in the body representation (last two equal). When I evaluate my move, my tail cell (old body[-1]) is free UNLESS my current body has last two equal (I just ate last turn) — and that's independent of whether I eat this turn! Because eating this turn duplicates body[-2]... 

Hmm wait, let me redo. Old body: [H, b1, b2, T]. If I eat this turn: new body = [newH, H, b1, b2, b2]. Length 5. Cells occupied after this turn's move: newH, H, b1, b2. T is free. Correct — the "tail stays" happens NEXT turn, when the duplicated b2,b2 means tail cell stays.

Hold on, but then where's the new segment? "新的一节加在尾巴上" — added at the tail. The representation [newH, H, b1, b2, b2] has the tail duplicated. So the snake's length went 4→5 but occupied cells are still 4 cells (newH, H, b1, b2). OK.

If I don't eat: new body = [newH, H, b1, b2], length 4. Occupied: newH, H, b1, b2. Same occupied cells!

Interesting — so occupied cells after my move (excluding newHead) = old body[0..len-2] in BOTH cases. The difference is next turn. So for collision checking THIS turn, eating doesn't change my tail behavior. The "tail stays" only manifests the turn AFTER eating, detectable via body[-1]==body[-2].

Great, this simplifies: 
blocked_this_turn (per snake s) = s.body[0..len-2] ∪ (s.body[-1] if s.body[-1]==s.body[-2] else ∅).

So cells that are fatal for my newHead: out of bounds, or in blocked_this_turn of any snake (including mine), or head-to-head with ≥-length snake (uncertain), or newHead == other snake's possible new head cell where they're longer/equal.

Also head-on with strictly shorter snake: I survive (they die) — even good. But careful: their dead body disappears, so no issue.

Now the "uncertain tail" thing: if another snake just ate (visible), their tail stays — handled. If they eat THIS turn, their tail stays only next turn. So following a tail is always safe this turn! Great, no uncertainty about tails this turn. Wait, but next turn if they ate, their tail stays — that's for next turn's evaluation. OK good. Tails are always safe to enter this turn (given current body doesn't show duplicated tail). Nice, cleaner than I feared.

Hmm wait, one more check on rule: "尾巴在第 1 步已经缩回，所以可以跟着别人的尾巴走；但刚吃过食物的蛇尾巴不动。" Yes consistent.

Now head-on risk: for other snake s, s's possible new head cells = 4 neighbors of s.head, minus its neck-reverse. If my newHead is among them and s.eff_len >= my.eff_len → potential death. eff_len = length + (1 if their candidate new head is on food) — for me, if newHead on food my len+1... Actually careful: does eating affect length at collision-time? Order: move → hunger → eat → eliminate. Yes, growth applied before elimination. So eff lengths: mine = len + (newHead on food), theirs = len + (their new head on food, which if their new head == my newHead and there's food there, both +1). Compare: if their_eff > my_eff → I die if they move there. If equal → both die. If less → they die, I live.

Since I can't know their move, treat cells adjacent to other snakes' heads with len>=mylen as risky (my death possible). Penalty approach: subtract large value if risky; but if the move is essential (only non-fatal move), take it.

Actually, better: compute probability-ish. Most snakes avoid head-ons too. But strong opponents might take a 50/50 when longer. Conservative: treat as risky, avoid when alternatives exist.

Corner trap: cells where my flood-fill space is small → death spiral. Flood fill from newHead treating my new body (after move, with growth if eating) and others' current bodies (post-tail-retraction) as walls. Count reachable. Also could do "component size vs my length" check: if reachable < my length + something, bad.

Refinement: flood fill counting other snakes' head-adjacent cells? Keep it simple: flood fill area; also track whether area contains food.

Move scoring:
score = 0
- if fatal → score = -inf (tier drop)
- risky head-on (snake with len ≥ my len can enter): score -= 60 (avoid strongly)
- area = flood fill count; score += min(area, some cap) * weight; if area < my_len: heavy penalty.
- food: dist to target food (use BFS distance through free space? Manhattan is cheaper; BFS through non-blocked cells is better). Use BFS from newHead to nearest food / chosen target food.
- health urgency: if my_health < 40, weight food more.
- prefer moves that keep distance from bigger snakes' heads (avoid being cornered by them next to their head).

Let me think about the food target choice: nearest food by BFS from my head (through passable cells). Among foods, consider "ownership": count of other snakes closer to it than me. Prefer foods where I'm closest. If health low, take nearest regardless.

Also survival: at very low health (< distance to nearest food + margin), must beeline food.

Also consider: in FFA endgame with few snakes left, similar logic applies.

1v1 specific tactics: when both snakes survive long, length decides → keep eating safely, contest food. Also cutting off opponent: if I'm longer, I could try to approach their head to restrict their space. That's advanced; a decent approximation: prefer moves that reduce opponent's flood-fill area / keep me between them and food. Might skip; flood fill + food greed is decent.

Actually one strong 1v1 tactic: when I'm longer and near the opponent's head, moving adjacent to their head forces them away (they fear head-on). Could implement lightly: bonus for reducing their accessible area. Let me add: compute opponent flood fill area after my move (approx, from their head, treating my new body as wall), prefer moves that reduce it when I'm longer. This is aggressive space control. Cost: 3 more flood fills per turn. 15x15 = fine.

Time complexity check (FFA, 31x31): per candidate move (≤3 after neck filter... wait 4 neighbors minus neck = 3): flood fill ~961 cells → 3 fills = ~3k ops, trivial. Plus opponent flood fills in FFA (10 opponents × 3 = 30 fills = 30k ops) still OK in 50ms Python? Python ~10M simple ops/sec... 30k ops with set/dict overhead — should be fine, but let's be careful; maybe only do opponent-space control in 1v1 (2 snakes).

Actually, let me also use flood fill "area" more cleverly: penalize moves where area < my_len + 2 (death trap), prefer larger area.

Another consideration: tie-breaking length at end. If game reaches turn limit with multiple survivors, length ranks. So when safe, eating is good. My default: pursue food when health < 95 (i.e., almost always), but weigh safety.

Also spawn safety: at start with stacked bodies, flood fill etc. still works.

Edge case: what if no non-fatal move? Then pick least bad: maybe a "risky head-on" cell hoping they don't move there (if snake is equal length, we both die — still better than certain death). Order of preference: non-fatal > head-on risky vs equal/smaller (if smaller, I survive their entry!) — wait if their len < my eff len and they enter, they die and I live. So vs smaller snakes, head-on cells are actually fine-ish (I survive). Only vs ≥ len they're fatal. If they don't come, no collision at all. So risk only matters vs ≥. But careful: equal → both die; that's a loss. So risky vs equal or longer.

Hmm, also "could they enter the cell" — the cell must be a valid move for them (not their neck-reverse, not fatal for them necessarily). Just consider adjacency.

Also avoid cells adjacent to longer snake heads even if not equal cell? E.g., if I move to a cell adjacent to a longer snake's head, next turn they might... that's normal play. Flood fill from there covers connectivity. Add small penalty for being within distance 1 of a longer snake's head (they threaten head-on next turn unless I'm near my... whatever). Actually being adjacent to longer snake's head is dangerous next turn too. Small penalty.

Let me also handle "eating when opponent also about to eat same food" — the head-on rule handles same-cell. If food is in contested area, I might eat it while they're 2 away — fine.

Let me think about the health vs food threshold. Each turn health -1. If health drops to 0 → die. If my BFS distance to nearest reachable food is d, I'm safe while health > d + small buffer. When health < d + 15, emergency: maximize eating probability — weight food strongly, accept slightly risky moves.

Food preference scoring among foods: score_food = dist_me - 0.7*dist_nearest_other? Hmm. Let me do: for each food, d_me = BFS dist from my head; d_other = min over other snakes of BFS dist from their head (BFS from each food to all cells once — multi-source? I need per-snake distances). Cheaper: BFS from each food outward until I find all snakes' heads? With 12 foods on 31x31 that's 12 BFS ≈ fine. Or simpler: BFS from each snake head to all foods. 11 snakes → 11 BFS full-board = 11k cells ≈ OK. Total per turn maybe 50k-100k basic ops — Python can do this in ~50-100ms? Hmm, risky. Let me estimate: a BFS over 961 cells with deque and set ops ≈ maybe 1-2ms in CPython. 11 BFS = 20ms. Plus 3 flood fills. Plus overhead. Might exceed 50ms in FFA late game. Need to be careful!

Optimization: use Manhattan distance approximations for food ownership in FFA; use BFS only for my own distance (1 BFS from my head). That's cheap and mostly fine. Walls only matter in tight spots.

Plan per turn:
1. Build grid sets: occupied_strong (cells fatal), per-snake info.
2. Candidate moves.
3. For each candidate: check fatal, compute risk (head-on), flood fill area (from newHead with new body as walls).
4. BFS from my head (or from each candidate newHead? BFS from my head gives distance to foods; candidate moves change distance by ±1; but path may be blocked. Simpler: one BFS from my head over free cells gives dist for all foods; then candidate move value = 1 + dist_from_neighbor... not exactly monotone if blocked. Alternative: for each candidate, quick check: if area flood fill already computed, run BFS inside flood fill simultaneously? Actually do flood fill BFS from newHead and record distance to nearest food in same BFS! One pass per candidate: BFS from newHead over cells not blocked, get: area count, nearest food dist, maybe also which foods reachable. 

But food beyond walls unreachable via BFS — then food dist = infinity for that food; fall back to Manhattan? If food unreachable from newHead, don't chase it. Choose target = food with min BFS dist overall (across candidates? evaluate per candidate: nearest food dist reachable from that newHead).

Contested food: for each food, Manhattan dist from other snakes' heads (approx, ignoring bodies). If min_other_manhattan < my_bfs_dist... Manhattan underestimates their distance, so if my_bfs <= min_other_manhattan, I'm strictly closer or equal. Prefer such foods. Compute a target food first (from my head, one BFS): choose food minimizing (my_bfs_dist + 3*(contested penalty)), then for each candidate move, score by whether it decreases BFS-dist to target from newHead. To get BFS dist from newHead to target, I can precompute a full BFS distance field from the target food! One BFS from target food over free cells → dist to all cells including each candidate newHead. 

So: pick target food (using BFS from my head to all foods — one BFS gives dist to all foods; plus Manhattan of others to each food for contention). Then BFS from target food → distance field. Candidate move score uses field[newHead]. That's 2 BFS + 3 flood fills per turn. Cheap.

Emergency mode (health low): target = nearest food by BFS; if unreachable, nearest Manhattan.

Hmm, but also multiple foods: nearest might be heavily contested while another is free. Target selection: for each food f: my_d = bfs_me[f]; other_d = min manhattan from other heads; if other_d < my_d → contested (likely stolen or head-on risk near it). cost = my_d + (8 if contested). pick min cost. Also add: prefer foods not adjacent to longer snake's head region... the contested check mostly covers.

Also growth value: eating is good for ranking and head-on strength. When health full-ish (e.g., > 90), eating still beneficial but safety weight higher. When health mid, normal.

Now flood fill details: treat as walls: my new body (all cells) + other snakes' current blocked cells (body[0..len-2] + tail-if-duplicated). Also, other snakes' heads: they'll move, but conservatively include their head-adjacent possibilities? Standard approach: flood fill counting cells, walls = all snakes' bodies (post-move approximation). Not including their future head positions (unknown). But a subtlety: cells adjacent to other snakes' heads might become blocked next turn; if my only escape is through such a cell... fine, approximation.

Flood fill from newHead: if newHead itself is in walls → area 0.

Area interpretation: if area < my_len → likely death trap soon. Score: min(area, cap)*w with cap ~ maybe 2*my_len+10? Prefer bigger areas. Also "articulation awareness" — proper bots use "fill to length" heuristics. I'll use: if area < my_len + 2: big penalty proportional; else moderate preference for area.

Actually a decent known heuristic: space_score = min(area, needed) where needed = my_len + K. And prefer moves toward more open space when no food target.

Also add tie-breakers: prefer continuing straight? Or slight randomness for unpredictability. Small random jitter to avoid deterministic loops with other bots (two bots mirroring each other forever). Add tiny random noise.

Also avoid 180 fallback: never return reverse of my current direction (neck). Compute my previous direction from head-neck.

Let me now also handle a subtle: "掉头无效，按原方向继续走" — if a bot returns U-turn, engine moves it straight. I'll never do that.

Deadlock/loop avoidance: if I keep circling with full health while food contested... fine.

1v1 special: also consider trapping. And important: in 1v1, when opponent dies I win immediately. If I'm longer, aggressive head-on pressure is strong: cells adjacent to opponent's head become "I survive" threats. But keep conservative.

Let me consider the "hunt smaller snake" behavior in FFA: when I'm much longer than another snake, moving into a cell adjacent to their head threatens head-on they'd lose. Not needed explicitly; head-on-risk logic naturally lets me take contested cells vs shorter snakes.

One more survival heuristic: avoid moving into a cell where ALL my next-turn moves would be adjacent to a longer snake's head... too deep. Skip.

End-game (FFA, few snakes left, e.g., 2 left): same as 1v1 logic.

Also the time-limit endgame: if turn > max_turns - small and I'm alive with health fine, just survive (avoid all risks, don't chase food unless very safe). Length only matters vs survivors; if I'm the longest survivor already, pure safety. Implement: if turns_left < health - 5 (I can survive to end without food): switch to safety mode (risk aversion up, food weight down) but still eat if free food on path. Actually eating when safe also adds length insurance. Keep food weight small in safety mode.

Hmm wait — important ranking subtlety: dead snakes rank by death time; among survivors, by length. If I'm in FFA and it's likely others die, surviving matters most. Safety first always.

Let me also implement a "look-ahead danger" for tail-following: when following a tail, if that snake... fine.

Now, code structure:

```python
import random
from collections import deque

DIRS = (("up",0,-1),("down",0,1),("left",-1,0),("right",1,0))

def decide(state):
    try:
        return _decide(state)
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        return "up"
```

_fallback: compute head, neck; pick first dir that's in-bounds and not into my own body[0..len-2] (cheap check, ignoring others). 

_decide:

```python
def _decide(state):
    w=state["width"]; h=state["height"]
    me_id=state["you"]
    snakes=state["snakes"]
    food=[tuple(f) for f in state["food"]]
    me=None
    for s in snakes:
        if s["id"]==me_id: me=s
    my_body=[tuple(p) for p in me["body"]]
    head=my_body[0]; neck=my_body[1] if len(my_body)>1 else head
    my_len=len(my_body)  # or me["length"]
    my_health=me["health"]
    others=[s for s in snakes if s["id"]!=me_id]
    
    # blocked: cells fatal to enter this turn
    blocked=set()
    for s in snakes:
        b=[tuple(p) for p in s["body"]]
        L=len(b)
        for p in b[:-1]: blocked.add(p)
        if b[-1]==b[-2]: blocked.add(b[-1])
```

Wait — for MY OWN move: my new head can't be on my body cells... my own body[0..len-2] — but my tail (b[-1]) is free unless duplicated. But careful, my new head == my old tail cell: I move onto my tail as it retracts — allowed ("尾巴在第 1 步已经缩回"). Yes, blocked set handles it.

But wait — what about the case where my body is length 3 stacked at spawn: b = [c,c,c]. blocked = {c} (b[:-1] = {c}, duplicated also c). Moving away fine.

Also note others' heads in blocked (they're b[0], included in b[:-1]). Their head cells: could I move into their head's old cell? After they move, old head cell is their neck — occupied. So yes, blocked. Correct.

But there's an edge: a snake of length... if other snake's body is [H, H, H] stacked (spawn), blocked = {H}. If I move adjacent to their spawn cell... their head moves somewhere, old cell remains occupied (3 cells → 2 cells? they move: new body = [newH, H, H]... wait after move: [newH] + old[:-1] = [newH, H, H]. So cell H still occupied. Yes blocked={H} correct for this turn. But next turn: [newH2, newH, H] — H still occupied. Fine.

Hmm wait, actually there's a subtlety with stacked spawn and "b[-1]==b[-2]": at spawn, body [c,c,c] means "just ate"? The engine just spawned them that way. So tail won't move — but all segments are same cell so irrelevant.

Head-on risk computation:

```python
    # my effective length if I eat: length +1 when comparing head-on
    # For each candidate cell, risk if an other snake with eff_len>=my_eff_len could move there
    other_heads=[]
    for s in others:
        b=[tuple(p) for p in s["body"]]
        oh=b[0]; on=b[1] if len(b)>1 else oh
        other_heads.append((oh,on,len(b),b))
    foodset=set(food)
```

For candidate newHead nh:
- my_eff = my_len + (1 if nh in foodset else 0)
- risk = 0; fatal_due_headon? Not fatal certain — probabilistic. risk value: for each other (oh, on, olen, ob): if manhattan(oh, nh)==1: their possible move to nh requires nh != their neck cell (nh != on). their_eff = olen + (1 if nh in foodset else 0) — if they move to nh and nh has food, they eat → olen+1. If their_eff > my_eff → they kill me → risk big (say risk=1). elif their_eff == my_eff → both die → risk big (1). else → they die, I survive → risk small (0.1? plus I might get food... actually if both heads at nh with food, both eat, then they die, I keep food). minor.

Also: what if other snake's head is ADJACENT but their move to nh is their neck-reverse (nh == their neck)? Then they can't move there (invalid → they go straight elsewhere). So exclude nh == on. Hmm, but their "straight" could also be nh if... their straight direction = oh - on. If nh == oh + (oh-on) and also manhattan(oh,nh)==1 → nh is not their neck cell so it's a valid move for them. Covered by adjacency check (any adjacent cell except their neck). Their possible new heads = 4-neighbors of oh minus their neck cell. So risk if nh in that set.

Wait, also their possible new heads include cells that would be fatal for them (walls) — they won't go there (any sane bot), but a bad bot might. Ignore.

Flood fill for area:

```python
def flood(nh, my_newbody_walls, blocked_others):
    # walls: blocked cells + my new body cells (except nh)
    ...
```

Let me define walls_for_flood = blocked ∪ {my body cells} — hmm, my new body = [nh] + my_body[:-1] (cells). The union with blocked already includes my body[0..len-2]. My tail cell: free (unless duplicated, in blocked). So walls = blocked ∪ {nh}? Since after my move, my occupied cells = nh + my old body[0..len-2] ⊂ blocked ∪ {nh}. Yes! walls_for_flood = blocked | {nh}. Nice and simple.

flood area from nh over cells not in walls, 4-connected, bounded by board.

Also I want BFS dist to target food from nh. Approach: BFS from target food cell tf over cells not in blocked (NOT including nh as wall — my head will move away... approximate; using blocked-only field, dist to nh approximates path length). Compute field once: BFS from tf over free cells (blocked as walls). Then per candidate: fooddist = field.get(nh). Combined with flood area per candidate.

But BFS from tf must use this turn's blocked; my head position as wall or not? My head moves this turn, so my head cell is free (it becomes... wait my old head becomes my neck — occupied! Hmm: after my move, my occupied = nh + old body[0..len-2], which includes old head. So old head cell is blocked this turn — it IS in blocked (b[:-1] includes b[0]). So BFS from tf through cells not in blocked: my head cell is a wall, my nh not yet... For distance-to-food-via-nh: path nh → tf shouldn't pass through my old head (it's occupied this turn) but can next turns. Approximation fine.

Alternatively simpler and consistent: compute per-candidate flood-BFS from nh (walls = blocked|{nh}) and record nearest food distance within the same BFS. But then the "target food" selection: pick target first via my own BFS from head.

Let me simplify to this per-turn algorithm:

1. Compute blocked.
2. BFS from my head over free cells (free = not blocked), giving dist_me to all cells. Get dist to each food. (My head cell itself is blocked; BFS starts from head, expanding to neighbors not blocked.) Note: nh candidates are exactly the neighbors of head, so dist_me field at nh = 1.
3. Choose target food: for each food f with dist_me[f] finite: cost = dist_me[f] + contention(f). contention = 6 if some other snake's Manhattan(head, f) < dist_me[f] (they're likely closer/equal) else 0. Also if food is unreachable (infinite), exclude (or use Manhattan*2 as cost). Pick min cost food as target. Emergency mode: if my_health < dist_me[min food] + 12 → must chase nearest reachable food hard; if none reachable... tough: pick nearest by Manhattan and hope (or just survive; if health will run out, maybe take head-on risks? If I starve in k turns, taking a 50% head-on vs certain death eventually... only when health really low, say < dist+3).
4. Compute dist field from target food (BFS over not-blocked cells) — or reuse: I can BFS from target food to get field_t; candidate fooddist = field_t[nh].
5. For each candidate dir (not neck-reverse, in bounds):
   a. nh.
   b. fatal if nh in blocked. Also treat "nh == wall" earlier.
   c. flood fill area from nh (walls = blocked | {nh}); count = area; also within flood, note if target food reachable & dist (BFS from nh with walls=blocked|{nh}, stop at target food or flood complete). Actually combine: do the BFS from nh, tracking dist to target food and area count simultaneously (full flood = area; stop early if found food? Need full area anyway for trap detection; 961 cells fine).
   d. head-on risk as above.
   e. score:
      - fatal → -1e9.
      - head-on risk (vs ≥) → -400 (huge, but above fatal). Maybe scale: vs strictly longer → -500; vs equal → -450 (both die = as bad as dying). Hmm both die: I die. Same. -500 both. vs smaller: -5 (fine, they die).
        But wait: if their move to nh is their ONLY... I can't know. Keep big penalty.
      - area: if area < my_len + 2 → penalty (my_len+2-area)*30 (trap). Else + min(area, cap)*2 where cap maybe 60? Let me think: area matters mostly as binary "enough room". Prefer larger: + min(area,120)*1.5.
      - food: - field_t[nh]*food_weight. food_weight depends on health: if health > 85: 1.0 (mild, still grow); mid: 2.0; urgent (health < field_t-based dist + 20): 4.0; critical: 6.0.
      Hmm, but always chasing food has a cost: it takes me to contested center. The contention penalty in target selection handles some. Also note eating keeps health 100 which is required anyway (must eat every ~90 turns). Default weight ~2 is fine.
      - small penalty for proximity to longer snakes' heads: for each other with olen >= my_len: if manhattan(nh, oh) == 1: -25; ==2: -6. (encourages space). But careful not to paralyze.
      - tiny random jitter ±0.3.
6. Choose max score. If all fatal → fallback chain: choose min-risk fatal? Just return any in-bounds non-neck move (straight preferred). Return straight if valid else any.

Additional: immediate-eat bonus: if nh on food: + small bonus (food weight × 1 dist saved) — the field_t[nh]=0 handles it naturally.

Also: don't step ONTO food when health is full and... eating is always good (length up). Always fine.

Edge: when field_t[nh] is infinite (target unreachable from nh) but reachable from another candidate: food_weight × big_dist. Use large dist (e.g., 9999 → dominates badly). Hmm, but if target unreachable everywhere, maybe pick another target? Let me compute field_t; if no candidate has finite field_t, retarget to nearest Manhattan food with weight small. Simplify: score food term = field_t[nh] if finite else 30 + manhattan(nh, tf).

Also flood fill area cap and the food chase conflict: if food is in a dead-end pocket smaller than my length, area penalty saves me. 

Emergency starvation handling: if health low (<= 25): boost food weight to 6-8; accept head-on risk vs equal-length? Both-die is a loss same as starving later... Actually if I starve in 5 turns and risk=50% death now: expected death turn 12.5 (50% now, 50% later-ish) vs certain death turn 5 — take risk. So when health < dist_to_food + 4 or health < 15: reduce head-on penalty to like -150 (vs fatal -1e9 still avoid certain death; risky cells become acceptable if much better food). Implement: dynamic headon_pen = 500 normally; if health < min_food_dist + 6 → 150; if health < 12 → 60.

Hmm, but "risk" isn't a coin flip — the other snake might not move there (probably won't if it risks them). vs equal-length snake: they also die → they avoid. So actual risk maybe 20-30%. OK with penalties as chosen.

Now the opponent-space-control (1v1 aggression): skip or add lightweight? Time budget allows: in 1v1 (num_snakes... but snakes alive could drop to 1? if only me alive, game over — decide not called? "只剩 1 条" ends game. But careful: decide might be called with only me? No—game ends. Also maybe called when I'm dead? No.) In 1v1 with 1 opponent: compute opponent flood area from their head with walls = blocked | {their head} — but my move affects it minimally (my nh occupies one cell). Bonus if my nh reduces their area: score += (base_opp_area - opp_area_after)*k. opp_area_after: flood from their head with walls = blocked | {nh} | {their head}. Cost: 2 extra floods. Cheap. Weight k=2 when I'm longer, 0.5 when shorter? When I'm longer, squeezing them is winning play (they may starve/get trapped, then I win by survival). But careful about overcommitting. k=1.5 when longer. Hmm — also risk: chasing them neglects food/health. Let me add mild weight: if my_len > olen + 2 and my health > 40: score += (opp_base - opp_new)*2. This rewards cut-offs without changing basic behavior much.

Actually, let me reconsider — is this worth complexity/bug risk? Mild benefit in 1v1. I'll include it; it's straightforward.

Also FFA: similar squeeze on nearest snake? Skip — 10 snakes, too costly-ish, and crowding is natural.

Also add: avoid being adjacent to two longer snakes... covered by penalties.

Tail-chasing safety: when no good food move and health fine, follow own tail (guoyou-like). The scoring with food weight ~2 will chase food anyway. If food unreachable/contested, area maximization gives tail-following-ish behavior. Fine.

One more important case: start of game FFA — snakes stacked, 12 foods, health 100. Standard chase works.

Potential pathology: two bots target same food, both arrive same turn → head-on. My head-on risk check marks food cell risky if opponent (≥ len) adjacent — at the final approach step, the food cell is adjacent to both heads; if opponent ≥ len, I get -500 → I veer off, they take it. If I'm longer, I proceed (their risk). This yields reasonable behavior: longer snake claims contested food. Equal length: both veer off → food sits there → loop? Both veer, then re-approach... deadlock possible but turn limit handles; also random jitter breaks symmetry eventually. Maybe equal-length: penalty slightly less (e.g., -450) so sometimes I take it (gamble)? If both gamble simultaneously → both die. Expected: with penalty equal for both deterministic bots... variance is better than certain starvation. Actually if both always veer, nobody eats, health decays, eventually emergency mode lowers penalty → someone takes it. That's emergent and OK.

Let me also double check the "simultaneous food" rule: both heads on same food cell both eat, then head-on elimination: longest survives (with food growth applied). Yes handled.

Another rule detail: "头撞到任何一条蛇的身体（除蛇头以外的任意一节，包括自己的）" — my blocked set = all body cells except... it says heads excluded from "body collision" (head-head handled separately). My blocked includes other snakes' heads (b[0]) — but entering another snake's head's NEW cell is the head-on rule, not body collision. Entering their OLD head cell: after they move, old head = their neck = body cell → body collision death. So old head cells are fatal — included in blocked via b[:-1]. ✓.

What if another snake dies this turn (starves at 0 or hits wall)? Dead snakes removed before my collision check? Order: (a) out of bounds die, (b) health 0 die, (c) body collisions die, (d) head-on. All simultaneous-ish? "淘汰（同时判定）" — all elimination conditions judged simultaneously. So if opponent hits a wall, their body still exists for my body-collision check this turn? Hmm, "同时判定" suggests yes: I check collisions against bodies of all snakes including ones dying this turn. But next turn they're gone. Does it matter? If opponent's body is on my path and they die this turn — I'd still die (simultaneous judgment). My model treats their body as wall this turn: safe/conservative. ✓. Edge: opponent at health 1 (will starve this turn). Their body cells: still fatal this turn. Next turn gone. OK.

Also dead snakes disappear → food respawns on random empty cells. No info needed.

Health 0 edge: "生命值降到 0：饿死" — happens after -1. So health 1 now → 0 → dead. I must eat when health would hit 0? If I eat this turn, health → 100 before starvation check. So eat on health 1 survives. My emergency thresholds give margin.

Now let me also double-check head-on vs my own food-eating length: I compute my_eff = my_len + (nh in food). And theirs if they enter nh: also eat same food (nh in food → their_eff = olen+1). Compare my_eff vs their_eff — note if nh has food both get +1 → equivalent to comparing base lengths. Fine.

Also: length from state["length"] vs len(body)? Should be equal. Use len(body) (safer, since body is ground truth). Hmm, example: length 4, body has 4 entries. Stacked at spawn: length 3, body 3 entries. After eating, does "length" increment and body show duplicated tail? Yes per rules. So len(body) == length always. I'll use len(body).

Now flood fill implementation, performance:

```python
def flood_fill(start, walls, w, h, stop_at=None):
    if start in walls: return 0, None
    seen = {start}
    dq = deque([start])
    while dq:
        c = dq.popleft()
        x,y = c
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(x+dx,y+dy)
            if 0<=n[0]<w and 0<=n[1]<h and n not in walls and n not in seen:
                seen.add(n); dq.append(n)
    return len(seen)
```

For area + food dist in one BFS:

```python
def bfs_area(start, walls, w, h):
    # returns (area, dist_to_foodmap?) 
```

Let me write a combined BFS from nh: walls = blocked | {nh}; track dist to target food cell (if target food in this component). Return (area, fooddist_or_inf).

For dist field from target food: BFS from tf with walls = blocked (food cells aren't blocked). field dict.

Per-turn BFS count: 1 (dist from my head to foods... wait do I even need this? I could BFS from each food... hmm). Let me restructure:

- foods list. For target selection I need dist_me(f) for all f. BFS from my head (walls=blocked, but head itself is in blocked... start BFS from head's neighbors: dist 1) → gives dist to all foods. One BFS. ✓
- Then target tf. BFS from tf (walls=blocked) → field. ✓ (dist from any cell to tf approx; symmetric since static walls.)
- Per candidate: flood BFS from nh (walls=blocked|{nh}) → area + dist to tf within component (from nh's BFS, or from field: field[nh] if tf's component... careful: field BFS from tf treats my old head as wall (it's in blocked); nh's flood also uses blocked|{nh}. Both use same walls minus nh. field[nh] is the graph distance ignoring that my body will also occupy nh... good enough. Actually I can just use field[nh] and skip tracking food dist in flood. But if nh not in field (different component), inf → handle with fallback dist = 50 + manhattan.)

So per turn: 2 BFS + up to 3 flood fills + (1v1: +2 floods). Very fast. 

Actually wait — there's redundancy: field from tf already gives distances; candidate scoring uses field[nh]. And dist_me to foods came from first BFS. Could combine: BFS from head gives dist to foods; then BFS from chosen tf. Fine, keep.

Hmm, one subtlety: target food chosen via dist from head; but candidate nh might be closer to a DIFFERENT food. Minor inefficiency; acceptable.

Emergency retarget: if health < 30, target = nearest-by-dist food (ignore contention). Already: contention penalty constant 6; in emergency, drop contention. Let me define contention penalty c_pen = 0 if health < 30 else 6.

Also multiple foods equal: prefer one with larger... whatever, jitter.

Now the safety-mode endgame: turns_left = max_turns - turn + 1. If turns_left < my_health - 3 (I survive to the end without food): food_weight reduced (still take free food: weight 0.8), headon_pen increased to 800, trap penalty same. Also if I'm the longest alive snake... comparing to others: if my_len > max other len, survivors rank by length; extra length still good but risk not worth it: keep small food weight. Actually eating when free still adds insurance in case others grow. Weight 0.8 fine.

Hmm, actually let me reconsider food weight defaults. health>85 → weight 1.2; 50-85 → 2.0; 30-50 → 3.0; else 5.0. And safety mode override to 0.8. And headon_pen: normally 500 (equal or longer). Wait I realize there might be an issue: avoiding ALL cells adjacent to equal-or-longer snakes' possible moves might be overly restrictive in crowded FFA — with 11 snakes, many cells adjacent to some snake head. Penalty 500 vs food weight ~2 × dist ~20 = 40 and area ~ up to 120*1.5=180. Hmm, area term: min(area, 120)*1.5 = up to 180. A risky cell with huge area (180) vs safe cell with area 100 (150) + risk -500 → safe wins. A risky cell area 120 vs safe alternatives area 15 (trap, penalty (mylen+2-15)*30 could be huge) → risky might win. OK the balance: risk -500 vs trap penalty ~30/cell. Seems reasonable: avoid head-on unless alternative is trap-ish. In FFA early with 11 snakes length 3-5: trap penalty (len+2-area)*30: area 12 vs len 5 → (7-12) negative → area bonus only. Let me formalize:

area_term = min(area, 200) * 1.2, and if area <= my_len + 1: extra penalty (my_len + 2 - area) * 40.

So area 12, len 5: 14.4. area 120: 144. Risky big-open vs safe medium: -500 dominates → avoid risk. Safe small pocket vs risky open: pocket len+2=7, area 5: 6 - 80 = -74 + risky open 144-500 = -356 → pocket wins. Pocket area 3, len 7: 3.6 - 240 → very bad; risky -356 → risky wins. Good: prefer small pocket over head-on gamble, but not death pocket. Hmm, is that right? Pocket area 3 with len 7 = certain death soon (though tail movement gives wiggle... area counts free cells; snake of len 7 in area-3 pocket dies in ~3 turns unless pocket opens). Head-on 50/50 (really ~20-30%) better. OK.

One more thing: flood-fill overestimates safety (doesn't account for other heads moving in). Also cells adjacent to other heads within my component may be stolen. Fine.

Also, I should treat cells that another snake's head occupies... covered.

Let me also add: avoid moving into a cell where the ONLY exit is adjacent to a longer head? Skip — complexity.

Edge case: no non-fatal, all candidates fatal (blocked or wall or neck). Then: pick candidate that's in-bounds & not neck, prefer one that's only "head-on risky" (not in blocked): among candidates, compute risk; choose the one with minimal badness: not-in-blocked > in-blocked. Return that. If literally all 4 are neck-reverse... impossible (neck-reverse is 1 cell). If all moves fatal (walls/blocked), return straight (previous direction) — die gracefully.

Fallback function: robust minimal version.

Let me also think about the U-turn/neck check when body length... my_body length ≥ 2 always (start 3). neck = body[1]. If neck == head (stacked), no restriction.

Prev direction for "straight": dir = head - neck if head != neck else None.

Now let me also handle rare: state["snakes"] might contain only me? Game would have ended; but if called, just play normally (others empty lists fine).

Food count = snakes+1 — always ≥ 1 food. food list non-empty. But guard against empty (then no target: pure area maximization).

Now, opponent squeeze in 1v1: compute only when exactly 1 other snake alive (regardless of num_snakes — FFA reduced to 2 also benefits!). Condition: len(others) == 1. opp = others[0]. opp head oh. Base opp area: flood from oh, walls = blocked | {oh}. Per candidate: flood from oh, walls = blocked | {nh} | {oh}. gain = base - new. score += gain * k. k = 2.5 if my_len > olen + 1 and my_health > 30 else 0.8. Also when I'm shorter: 0 (don't seek confrontation) or even negative (keep distance)? When shorter, maybe avoid reducing their space (provokes aggression)? Keep 0.3 mild when shorter but healthy. Hmm, careful: gain can be large (cutting them from 200 to 20 = 450 points) which would override food/safety basics — is that OK? If I'm longer and healthy, cutting them IS great (they may die → I win outright / rank 1). But my own safety terms (fatal/trap) still guard me. But wait — the cut gain uses walls=blocked|{nh} which includes MY current body — the cut must be actually caused by my nh. It is: gain = area difference from adding nh. Fine. But also my head moving creates the block only this turn; next turn my head moves on. Real cuts need my body. The gain approximates "denying a region". OK mild k.

Also: should I reward eating food that opponent is closer to (denial)? In 1v1 length tiebreak, denial is valuable. Contested penalty already discourages; in 1v1, if we both survive to 500, length decides → stealing contested food is +2 swing. But head-on risk at food cell... The head-on penalty handles the arrival collision. The contention penalty c_pen=6 discourages approaching contested food. In 1v1 maybe reduce c_pen to 2 (food denial worth it). Set c_pen = 2 if len(others)==1 else 6.

Hmm, wait. There's a subtle issue with contention measure: other_d = min manhattan from other heads to food; my_d = BFS dist (≥ manhattan). If other_d < my_d → contested. If equal-ish, ambiguous. Manhattan underestimates them, BFS overestimates me slightly (walls). Eh, fine.

Let me now also double check the neck rule interplay with fallback: if my chosen move is neck-reverse — I filter candidates so never.

Another important detail: "掉头（走回自己脖子那一格）无效，按原方向继续走" — the engine handles bots that return invalid; I just never return it.

Now, let me think about whether flood fill should account for my tail movement making space behind me — the standard "space = area" works since my body is walls but my tail vacates as I move. The flood from nh with static walls overestimates available space for long-term survival (cells behind my body counted only if connected around). Since my body is a wall in flood, cells "behind" me are unreachable unless path around my body exists — correct-ish. But my body shrinks over time (tail moves), so pockets open. Overestimation risk exists but standard.

Improvement: "tail-time" flood fill (walls only if body cell's index < area time). Advanced; skip? It materially improves trap evaluation in tight spaces. Hmm. Given effort constraints, maybe implement a simple version: BFS from nh where a cell occupied by my body at index i (from head... tail index) becomes free at time t if t >= (len-1 - i) + 1 (tail retracts one per turn; cell i (0=head) frees after (len - i) turns... let me think: body cells [c0..c_{L-1}]. At turn t (t≥1), tail has retracted t times (assuming no food): occupied = c0..c_{L-1-t}. Cell c_i free at t ≥ L - i. BFS with time: dist d to reach a cell; cell passable if d >= L - i (for my cells) — plus other snakes' cells similar with their lengths. This is "time-aware flood fill". It's the proper way and not much harder: BFS state = (cell, time). Since BFS explores in increasing d, at each cell arrival time d; allow entering cell if not blocked-permanently (walls: none permanent except... other snakes also move/shrink; approximate their cells as free at d >= their L - i too, and their head-adjacent growth ignored).

This gives better area estimates in tail-chasing situations. Worth it? It changes flood fill to time-expanded BFS. Complexity similar (each cell visited once with earliest arrival time — since arrival times are monotone in BFS, one visit per cell is correct: first arrival is earliest). Cell passable if: not wall, and if occupied by a snake body cell with "free time" f, then need d >= f. Since we want area count... count cells reachable with the relaxed rule.

Hmm, but careful: my own nh occupancy over time — my body also MOVES (head extends into new cells). In time-aware fill, my body's future occupation is my choice — the fill is exploring possible futures; cells I'd occupy are the path itself. Standard approach: treat my current body cells as freeing at rate 1/turn from tail; ignore my future head extensions (optimistic). Acceptable.

Let me implement flood with pass-time:

precompute free_time dict: for each snake, for each index i, cell c: free_time[c] = min over occurrences of (L - i) where L = len(body)... but eating adds delays (tail stalls). Ignore eating (optimistic). Also for duplicated-tail snakes... i near tail: L-i small. Fine.

BFS from nh at d=0: neighbors entered at d+1. Passable if in-bounds, and (cell not in any body) or (d+1 >= free_time[cell]).

Wait, also cells occupied by other snakes' FUTURE heads — ignore.

Also blocked-head... fine.

But hmm: with free_time, "area" counts cells reachable eventually, which can make tiny pockets look fine (my tail frees up). E.g., area where I chase my own tail in a small loop — actually that's legitimately survivable if the loop is ≥ my length-ish. The time-aware fill captures this correctly-ish. This is good for the classic "survive in small space by tail-chasing". I'll use time-aware flood.

But also need a cap on search: BFS visits ≤ w*h cells. Fine.

Area semantic: number of cells reachable under relaxation. For trap detection: if area < my_len... with tail-chasing, could still survive. Use area with penalties as before; time-aware just gives better estimates.

Wait, one more consideration for free_time of other snakes: their tails free at rate 1/turn, but they EAT → stall. Optimistic for them (their cells stay longer, blocking me → I might overestimate my space? If I plan through their tail cell at time t but they ate, tail stays → I die). Slight risk. Alternatively add +2 delay to their free times as safety margin? Common trick: treat other snakes' free_time with +stall margin. Let me use their free_time + 1 or +2. Hmm — eating chance per turn is lowish (food density). Margin +2 reasonable? If their tail cell is my escape, I arrive exactly when freed... Let me add margin of 2 turns for other snakes' cells. Actually, hmm, but this can also block legitimate tail-following. I'll add margin 1... Let me think: their tail cell frees at t = L - i for index i. If they ate during those turns, delayed. Prob of a specific snake eating within next ~L turns is moderate (food respawn each turn eaten by someone). For safety in critical escapes I'd rather have margin. Use margin +2 for others, +0 for me. Hmm, but wait: for ME, eating also delays my tail! If I plan to eat (my target food), my tail stalls → my computed space shrinks. My own eating during the chase: if I grab food mid-chase, tail stalls 1 turn → tight tail-chase breaks. Margin for myself when planning to eat... complexity. Skip; margin 0 for me but the food-eat bonus may cause tight-loop deaths rarely. Actually, simpler: give myself margin +1 too when... no — let me just do others +2, me +0. Actually hmm, let me reconsider: with me +0, if I eat (which happens regularly when chasing food), my tail stalls and my flood-fill plan breaks. Let me give me +1 margin only if... you know what, margins are heuristics. others +2, me +1. It biases toward open space. Fine.

Actually wait, let me reconsider whether time-aware flood is worth the complexity and bug risk vs static flood. Static flood-fill from nh (walls = current bodies incl. tails retracted) is the classic; it underestimates space in tail-chase scenarios (treats own body as permanent wall) → overly conservative in tight spaces, refusing survivable pockets. Time-aware is strictly better info. Implementation is ~10 lines more. I'll do time-aware.

Also for area counting: count reachable cells (excluding nh start? include, doesn't matter much — use consistent).

Let me also make sure the BFS distance field from target food uses static walls (blocked) — that's for pathing, fine.

Now, head-on risk refinement: also consider snakes whose possible new head == nh where their move would kill me. I check adjacency (manhattan 1). But ALSO: what if nh is such that a longer snake's head could arrive at nh via their straight move only? All their moves are the 4 neighbors minus neck. All are manhattan-1. Covered.

What about a longer snake moving into the cell I'm LEAVING (my head cell)? Not my problem.

Now, code time budget re-check per turn (FFA worst): BFS head→foods (1), BFS tf→field (1), 3 × time-aware floods (each ≤ 961 cells × 4 neighbor checks with dict lookups) ≈ maybe 3ms each in worst case? Python set/dict ops ~100ns... 961*4 = 4k lookups per flood, trivial (<1ms). All good. Even ×10 overhead fine.

Opponent squeeze floods: only when 1 other snake. Fine.

Now write the final code carefully.

```python
import random
from collections import deque

DIRS = [("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0)]
DIRMAP = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def decide(state):
    try:
        mv = _decide(state)
        if mv in DIRMAP:
            return mv
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        return "up"


def _fallback(state):
    w = state["width"]; h = state["height"]
    me = None
    for s in state["snakes"]:
        if s["id"] == state["you"]:
            me = s
    body = me["body"]
    head = tuple(body[0])
    neck = tuple(body[1]) if len(body) > 1 else head
    blocked = set()
    for b in body[:-1]:
        blocked.add(tuple(b))
    if len(body) >= 2 and tuple(body[-1]) == tuple(body[-2]):
        blocked.add(tuple(body[-1]))
    best = None
    for name, dx, dy in DIRS:
        nh = (head[0] + dx, head[1] + dy)
        if nh == neck:
            continue
        if not (0 <= nh[0] < w and 0 <= nh[1] < h):
            continue
        if nh in blocked:
            continue
        return name
    # all bad: go straight if possible
    if head != neck:
        d = (head[0] - neck[0], head[1] - neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == d:
                return name
    return random.choice([d[0] for d in DIRS])
```

Hmm wait — fallback returns first safe by DIRS order — deterministic bias (up first). Add preference: straight first. Let me restructure fallback: order candidates: straight, then others. Fine.

Now _decide:

```python
def _decide(state):
    w = state["width"]; h = state["height"]
    turn = state["turn"]; maxt = state["max_turns"]
    me_id = state["you"]
    snakes = state["snakes"]
    me = None
    others = []
    for s in snakes:
        if s["id"] == me_id:
            me = s
        else:
            others.append(s)
    my_body = [(p[0], p[1]) for p in me["body"]]
    head = my_body[0]
    neck = my_body[1] if len(my_body) > 1 else head
    my_len = len(my_body)
    my_health = me["health"]
    foods = [(f[0], f[1]) for f in state["food"]]
    foodset = set(foods)

    # blocked cells this turn (fatal to enter)
    blocked = set()
    # free_time for time-aware flood
    free_time = {}
    for s in snakes:
        b = [(p[0], p[1]) for p in s["body"]]
        L = len(b)
        stall = 0 if s["id"] == me_id else 2
        for i, c in enumerate(b):
            t = L - i + stall
            if c not in free_time or t < free_time[c]:
                free_time[c] = t
            if i < L - 1:
                blocked.add(c)
        if L >= 2 and b[-1] == b[-2]:
            blocked.add(b[-1])
```

Wait — for duplicated tail (just ate): b[-1]==b[-2]; blocked includes b[-1]. Also its free_time should be later: indices L-1 and L-2 same cell; free time min taken → L-(L-2) = 2 + stall. Hmm, if just ate, tail doesn't move next turn, so cell b[-2] frees at... let me not overthink; min with stall margin approximates.

Hmm, actually wait: for MY OWN blocked set: b[:-1] includes my head b[0] and neck — correct, can't enter those. My tail b[-1] free unless duplicated. ✓.

For free_time of my own head/neck etc.: t = L - i; head i=0 → t = L. ✓.

Edge: stacked spawn body [c,c,c]: blocked={c}; free_time[c] = min(3,2,1)=1. Flood from nh can re-enter c at d>=1. ✓.

Other snake info for risk:

```python
    opp_info = []
    for s in others:
        b = [(p[0], p[1]) for p in s["body"]]
        oh = b[0]
        on = b[1] if len(b) > 1 else oh
        opp_info.append((oh, on, len(b)))
```

Head-on risk for candidate nh:

```python
def headon_risk(nh):
    my_eff = my_len + (1 if nh in foodset else 0)
    death_risk = 0  # number of snakes that could kill me here
    win_risk = 0
    for oh, on, ol in opp_info:
        if abs(oh[0]-nh[0]) + abs(oh[1]-nh[1]) == 1 and nh != on:
            o_eff = ol + (1 if nh in foodset else 0)
            if o_eff >= my_eff:
                death_risk += 1
            else:
                win_risk += 1
    return death_risk, win_risk
```

Time-aware flood:

```python
def flood_area(start, walls_extra):
    # returns count of reachable cells (time-aware), start must be passable now
    if start in blocked or start in walls_extra:
        return 0
    seen = {start}
    dq = deque([(start, 0)])
    cnt = 1
    while dq:
        (x, y), d = dq.popleft()
        nd = d + 1
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h:
                c = (nx, ny)
                if c in seen:
                    continue
                ft = free_time.get(c)
                if ft is not None and nd < ft:
                    continue
                if c in walls_extra:
                    continue
                seen.add(c)
                cnt += 1
                dq.append((c, nd))
    return cnt
```

Hmm wait, there's an issue: free_time cells are "blocked now but free later". Cells NOT in free_time and not walls_extra are free now. Cells in free_time with nd >= ft passable. ✓. But also `blocked` now-cell: any cell in free_time is currently snake body; passable later. Cells in blocked are those cells. OK consistent: blocked cells all appear in free_time (since I add free_time for every body cell). So the only permanent walls are out-of-bounds. walls_extra = {nh} etc.

Hmm, but should flood really let me pass through other snakes' body cells eventually? Their bodies persist (they keep moving); passing through where their body WAS at time t is valid if they've moved on. Their body cells free as they move... my free_time model assumes all snakes shrink in place, which is wrong (heads move forward, extending). Optimistic but standard. OK.

BFS distance from a source over currently-free cells (static):

```python
def bfs_dist(start, targets=None):
    # returns dict cell->dist for cells reachable from start through cells not in blocked
    # start itself may be in blocked (e.g., my head); handle by starting expansion from it anyway
    dist = {start: 0}
    dq = deque([start])
    while dq:
        c = dq.popleft()
        d = dist[c] + 1
        x, y = c
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h:
                n = (nx, ny)
                if n not in dist and n not in blocked:
                    dist[n] = d
                    dq.append(n)
    return dist
```

Start = my head (in blocked but we seed it). Then dist to foods = dist[food] if present.

Target selection:

```python
    dist_me = bfs_dist(head)
    min_food_dist = None
    reachable_foods = [f for f in foods if f in dist_me]
    # target selection
    target = None
    if foods:
        best = None
        for f in foods:
            dme = dist_me.get(f)
            if dme is None:
                dme = 999
            # others' manhattan
            doth = min((abs(o[0][0]-f[0]) + abs(o[0][1]-f[1]) for o in opp_info), default=999)
            contested = 1 if doth < dme else 0
            cpen = 2 if len(opp_info) == 1 else 6
            if my_health < 30:
                cpen = 0
            cost = dme + contested * cpen
            if best is None or cost < best[0]:
                best = (cost, f)
        target = best[1]
    if target is not None:
        min_food_dist = dist_me.get(target, None)
```

Hmm, if all foods unreachable (dme=999): target still chosen by cost (contested flag likely 0 since doth<999... doth manhattan < 999 → contested → cost 999+cpen vs another unreachable food cost 999. Prefer the non-contested? Manhattan-wise might matter little. Also maybe prefer nearest Manhattan as tiebreak. Let me include: cost = dme + contested*cpen + manhattan(head,f)*0.01 as tiebreak. Meh, keep simple.

Then dist field from target:

```python
    field_t = bfs_dist(target) if target is not None else None
```

Emergency determination: nearest reachable food distance dmin = min over reachable_foods of dist (may be None if none reachable). If my_health <= (dmin if dmin is not None else 15) + 6 → emergency (food weight high, headon_pen lower). Also if no reachable food and health < 25 → emergency-ish (head toward nearest Manhattan food? field_t gives none... use manhattan scoring).

Scoring per candidate:

```python
    turns_left = maxt - turn + 1
    safety_mode = turns_left < my_health - 3   # can coast to the end
    
    # weights
    if safety_mode:
        fw = 0.8
        headon_pen = 900
    elif my_health > 85:
        fw = 1.4
        headon_pen = 500
    elif my_health > 50:
        fw = 2.2
        headon_pen = 500
    elif my_health > 30:
        fw = 3.5
        headon_pen = 500
    else:
        fw = 6.0
        headon_pen = 300
    # emergency starvation: if dmin reachable and health < dmin + 6 → beeline
    if min_food_dist is not None and my_health <= min_food_dist + 6:
        fw = max(fw, 8.0)
        headon_pen = min(headon_pen, 120)
    if my_health < 12:
        headon_pen = min(headon_pen, 80)
        fw = max(fw, 9.0)
```

Hmm wait, careful with extreme emergency: if health 3 and food 5 away, I'm dead anyway unless... I die. Beeline and pray. If no reachable food and health < 20: fw=9, headon_pen=80: gamble toward nearest food by manhattan. field_t may be None-ish; handle food term via manhattan.

Candidate loop:

```python
    cands = []
    straight_dir = None
    if head != neck:
        v = (head[0]-neck[0], head[1]-neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == v:
                straight_dir = name
    for name, dx, dy in DIRS:
        nh = (head[0]+dx, head[1]+dy)
        if nh == neck and head != neck:
            continue
        if not (0 <= nh[0] < w and 0 <= nh[1] < h):
            continue
        if nh in blocked:
            continue
        cands.append((name, nh))
```

Wait, if head == neck (stacked), nh == neck never true since neck == head and nh is a neighbor. The condition `nh == neck and head != neck` — if head == neck, skip check. Actually if head==neck, nh (neighbor) ≠ head == neck. So `nh == neck` suffices. OK.

If cands empty → fallback path: return _fallback-ish: pick least bad (in-bounds, not neck) even if blocked; return straight if in-bounds else any. Let me handle: 

```python
    if not cands:
        # try risky (head-on) cells? cands excluded only walls/blocked/neck. All blocked → choose straight if in bounds else any in-bounds non-neck.
        for name, dx, dy in DIRS:
            nh = (head[0]+dx, head[1]+dy)
            if nh == neck: continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h:
                return name
        return random.choice(["up","down","left","right"])
```

Hmm — wait, actually cells that are only head-on-risky (not blocked) are already in cands. So cands empty means all in-bounds non-neck cells are blocked/walls → death this turn regardless → return straight (dies but whatever). Fine — but actually maybe a blocked cell that's another snake's tail-that-might... no — blocked set is exact per the rules (tail stays only when duplicated, which I detect). Hmm, wait — is it exact? Other snake eats THIS turn → their tail stays only NEXT turn (duplicated representation appears after this turn's eat). Right — eating this turn does NOT keep tail this turn (my earlier analysis). Let me re-verify once more with the example flow because it's crucial:

Turn t: snake body [H,b1,b2,T], no dup. Moves: [nH,H,b1,b2] (T freed). Eats food at nH: length 4→5, new segment at tail → [nH,H,b1,b2,b2]. So the tail cell T was freed this turn even though it ate. The duplicated b2 appears. Turn t+1: tail (second b2) doesn't move: body [nH2,nH,H,b1,b2]. So the "tail stays" effect is on turn t+1, and visible from body dup at start of t+1. ✓ So blocked set (computed from current body) is EXACT for this turn. 

But subtle: MY move onto another snake's tail cell — safe this turn. But what if they eat this turn and I'm... no wait, if they eat this turn their tail STILL frees this turn. The stall is next turn. So following tails is always safe the turn you enter. Next turn, if they ate, their tail cell (where my head now is... no wait — I entered their tail cell which is now behind... hmm: turn t: their tail T frees, I move into T. Turn t+1: their body is [nH,H,b1,b2,b2] (if ate) — the dup cell b2 is their tail-next-turn-not-moving; my head sits in T, which is not their body. Fine. If they didn't eat: [nH,H,b1,b2] wait that's if length... whatever. My head in T is not in their body either way, unless they... no. OK. Safe.

So cands nonempty normally. Good — but note the prompt says "但刚吃过食物的蛇尾巴不动" (tails of snakes that just ate don't move) — that's the visible-dup case handled in blocked. ✓

Score each candidate:

```python
    best = None
    for name, nh in cands:
        death_risk, win_risk = headon(nh)
        area = flood_area(nh, {nh})
        # hmm: walls_extra should include nh? nh is start. Others' future heads? no.
        score = 0.0
        score -= death_risk * headon_pen
        score -= win_risk * 5
        # area
        if area <= my_len + 1:
            score -= (my_len + 2 - area) * 40
        score += min(area, 220) * 1.2
        # food
        if target is not None:
            if field_t is not None and nh in field_t:
                fd = field_t[nh]
            else:
                fd = 60 + abs(nh[0]-target[0]) + abs(nh[1]-target[1])
            score -= fd * fw
        # bigger-snake proximity
        for oh, on, ol in opp_info:
            md = abs(oh[0]-nh[0]) + abs(oh[1]-nh[1])
            if md == 1:
                if ol >= my_len: score -= 20
                else: score += 2
            elif md == 2 and ol > my_len:
                score -= 4
        # 1v1 squeeze
        if squeeze_on:
            a2 = flood_area(opp_head, {nh, opp_head})
            score += (opp_base_area - a2) * squeeze_k
        score += random.random() * 0.3
        if straight_dir == name:
            score += 0.15  # tiny inertia to reduce dithering
        if best is None or score > best[0]:
            best = (score, name)
    return best[1]
```

Wait — issue with flood_area(nh, {nh}): the walls_extra {nh} — nh is the start; including it as wall for neighbors is fine (start already in seen). Actually the check `if c in walls_extra: continue` prevents re-entering nh. Good. But the start check `if start in blocked or start in walls_extra: return 0` — nh not blocked (filtered), so returns count ≥1. OK but careful: flood_area signature: walls_extra param includes nh. Let me just pass walls_extra set.

Hmm — one issue with the head-on risk & flood: even if a longer snake might enter nh, if they DON'T, my flood area is what I computed. The penalty approach is right.

But another subtlety: what if nh is adjacent to longer snake's head — meaning next turn they could cut me... the -20 proximity penalty covers.

Also — important: what about moving into a cell where an equal/longer snake's head is ALREADY... that's blocked (their head in b[:-1]). ✓

Now squeeze setup:

```python
    squeeze_on = False
    if len(opp_info) == 1:
        oh, on, ol = opp_info[0]
        opp_head = oh
        opp_base_area = flood_area(oh, {oh})
        if my_len > ol + 1 and my_health > 35 and not safety_mode:
            squeeze_k = 2.0
            squeeze_on = True
        elif my_health > 35:
            squeeze_k = 0.5
            squeeze_on = True
```

Hmm wait, flood_area(oh, {oh}): oh is the opponent's head — oh is in blocked (their body b[0] ⊂ b[:-1]). My flood_area returns 0 if start in blocked! Need a variant where start allowed despite blocked. For my own candidates, nh not blocked. For opp head, it is. Let me adjust flood_area: remove the blocked-start check (start is just a position; treat as passable seed). Since I filter cands for blocked already, fine.

But hmm — opp flood with walls {oh}: their head cell itself shouldn't be re-entered... seen includes start. OK. Also should I include MY head... my head is in blocked/free_time anyway.

Wait, actually for opponent's area, using free_time means their body cells eventually open. Fine.

One more check on flood_area correctness: cells in free_time are currently-occupied; blocked cells ⊆ free_time cells (I set free_time for every body cell). So a cell in blocked but free later passes at nd >= ft. And nh's walls_extra handles my new head. But what about MY new body cells after this turn — my old body cells (blocked, in free_time with stall=0): they free at L - i from... my body will have moved; the free_time for my cells assumed static shrink — approximately right (my body follows my path... eh, optimistic). Standard.

Also flood needs to know that cells occupied by ME move with me... skip.

Potential issue: free_time uses min over snakes for shared cells (two snakes can't share a cell anyway, except transiently no). OK.

Now let me double check the head-on risk function uses my_eff vs their o_eff correctly, including when nh has food: both +1 — comparing (my_len+1) vs (ol+1) ≡ my_len vs ol. Fine.

One more head-on case: what if TWO snakes could enter nh? death_risk counts them; penalty scales. OK.

Also, what about a longer snake entering nh where nh is MY target food — I eat and they eat and collide: handled (both +1).

What about "both heads enter same cell" where the other snake is the one DYING (shorter)? I survive — win_risk. ✓

Now, an important gap: flood area doesn't account for other snakes taking cells in the future (they're moving too). In crowded FFA this optimism can kill me. Counterbalance: the area term capped at 220*1.2=264; trap penalties; risk penalties. I think fine for v1.

Another gap: I don't model that cells adjacent to opponents' heads will be contested NEXT turn (they move into my area). In FFA, being deep in a crowd is risky. The proximity penalties partially handle. OK.

Now think about opening behavior FFA: 11 snakes around a ring on 31x31, 12 foods. Snakes length 3 stacked. Health 100. Foods random. My bot: chases best food (contention via manhattan). Head-on penalties: with everyone length 3, equal-length adjacency → risk. At spawn, heads adjacent... snakes "沿一圈均匀排开" — spaced out on 31x31 ring, ~10 cells apart maybe. Fine.

Behavior check — potential dithering: food weight pulls toward target; if target contested, cpen=6 in cost selection picks less contested food. If I switch targets each turn (jitter), path oscillates. The 0.15 straight inertia + hysteresis? Could add: keep previous target if still reasonable. Let me store global _target; if previous target still exists and dist reasonable (≤ best cost + 3), keep it. Small addition, reduces dithering. Let me add.

Also global _last_dir for inertia is unnecessary (straight_dir computed from body).

Now, safety_mode: turns_left < health - 3 means I never need food again. But others may die before the end — ranking among survivors by length. If I'm longest survivor, safety. If a longer snake is alive and also coasting, they outrank me... I'd need food to pass them; risky. Compromise: safety_mode with fw=0.8 still takes FREE food (low risk). Keep.

Hmm, also: in safety mode should I still approach food? fw=0.8 mild pull. Yes.

Edge: max_turns 500/800, health 100 → coasting only relevant late if health high: turns_left < health-3 → e.g., health 95 → last 92 turns. OK.

One more: food eaten → respawn elsewhere random. No prediction. OK.

What about the "both snakes reach food same turn both eat" — when I'm longer and adjacent to contested food with equal... vs shorter snake: I take it (win_risk small penalty). ✓

Also consider: I'm equal length, food adjacent to both heads, other bot also conservative → both avoid → nobody eats. cpen selects other food eventually. Random jitter breaks loops. OK.

Now — timing check: worst case per turn: bfs_dist(head) ~961, bfs_dist(target) ~961, 3 floods ~961 each, squeeze: 1 + 3 floods. Total ~8k cell expansions × ~5 ops ≈ 40k ops → well under 50ms. Python function call overhead — fine. Even 10x margin OK.

Turn 1 has 1s limit — no special handling needed.

Let me also handle state anomalies: snakes list may not contain me?? If I'm dead, decide won't be called presumably. Guard: if me is None → return random dir. Also body could be length 1? Start is 3; can't shrink. But body list might have length... trust ≥ 2? Add guards (use len>1 checks everywhere).

Now let me also reconsider: `blocked` for other snakes includes their heads. But when checking candidate nh against `blocked` — if nh equals another snake's head cell — is that fatal? Their head moves away; old head cell becomes neck — occupied. So yes fatal. But WAIT: what if that snake dies this turn before moving? They still moved (movement happens first for all simultaneously). The body cell exists during collision judgment. Fatal. ✓. What if nh is another snake's head cell AND that snake fails to move... impossible, all move.

Hmm, actually one more: what if nh is a cell where the other snake's head currently is, and their new head also... irrelevant, nh occupied by their neck post-move → dead. ✓

Another subtle rule check: "头撞到任何一条蛇的身体（除蛇头以外的任意一节）" — head-head same cell is rule 4, handled separately. My blocked includes their head cell (their old head) — as neck after move — fatal ✓. Their NEW head cell = potential shared cell → head-on logic. ✓

Now, the case where the opponent might not move because they returned an invalid direction and engine moves them "原方向直行" — they still move somewhere. Their possible cells: 4-neighbors minus neck. Their straight move is one of them. Covered.

I think the logic is solid. Let me also think about flood area for candidate where nh would be... one more consideration: I should include, in flood walls, the cells that other snakes' heads could occupy next turn? That's the "contested region" idea. Skip.

Now, potential improvement: when no food reachable and health OK, behavior = area maximization + food manhattan pull. Fine.

Let me now also double-check `bfs_dist` from my head: my head is in blocked. Seeds dist[head]=0 and expands to non-blocked neighbors. My candidates nh are exactly non-blocked neighbors (also in-bounds). dist[nh] = 1. dist to foods: correct-ish paths avoiding current bodies. But paths through my own body cells (which free up) not allowed — underestimates reachability. Fine.

For field_t (from target food): BFS from target over non-blocked. nh in field_t → path exists around current bodies. If not, fallback fd = 60 + manhattan → effectively deprioritized. But my body cells block the field — e.g., food behind my own body reachable after tail moves — field says unreachable. Fallback 60+manhattan keeps mild pull. OK.

Now — emergency when NO food reachable: min_food_dist = None → emergency only via health < 12. And fw stays based on health tiers; target chosen among unreachable foods (dme 999, contested flags via manhattan < 999 → contested → cpen added... cost=999+cpen for all, min = least contested?? manhattan-based contested: doth (manhattan) < 999 → contested for ALL foods → all cost 999+cpen → tie → first food. Bad. Fix: when dme==999, use dme_manhattan for cost: cost = manhattan(head, f)*2 + contested... Let me restructure target selection:

```python
    for f in foods:
        dme = dist_me.get(f)
        if dme is None:
            dme_m = abs(head[0]-f[0]) + abs(head[1]-f[1])
            dm = 200 + dme_m   # unreachable penalty
        else:
            dm = dme
        doth = min((abs(oh[0]-f[0])+abs(oh[1]-f[1]) for oh,_,_ in opp_info), default=999)
        contested = 1 if doth < dm else 0
        ...
```

With dm=200+manhattan, doth < dm almost surely → contested. Hmm. For unreachable foods, maybe ignore contention: contested only when dme reachable. Simpler: contested = 1 if (f in dist_me) and doth < dist_me[f]. For unreachable, contested=0, cost = 200+manhattan tiebreak. OK.

Also for hysteresis: keep global _prev_target; if in foods and its cost <= best_cost + 2, keep.

Now think again about whether "area" via time-aware flood could make me suicidally confident: e.g., candidate nh enters a corridor behind a longer snake whose body fills it — free_time of their cells opens over time as they move... their body cells free at their shrink rate, but their head keeps EXTENDING (they move forward, so actually their body vacates cells faster than shrink-rate if moving away — free_time is conservative there; if moving TOWARD me/past me... their body occupies new cells). Whatever — heuristics.

Hmm, one more real danger: entering a cell that a longer snake will ALSO want (both flood areas overlap) — in practice, head-on penalty handles shared NEXT cells; overlapping regions later — unavoidable.

Let me also add: penalty for candidate nh that equals a cell ADJACENT to longer snake's head in their movement direction... covered by md==1 penalty -20. Plus the death_risk if they could ENTER nh (that's exactly md==1 from their head, i.e., nh adjacent to their head — same cells!). Wait — death_risk counts snakes with manhattan(oh, nh)==1 (they can enter nh). And the "proximity" penalty ALSO gives -20 for md==1 & ol>=my_len. Double penalty for the same thing — fine, extra caution vs longer snakes' heads (even if they can't enter nh... if md==1 they CAN enter nh unless nh==on). OK it's consistent; total ~-520 for risky cells. Good.

Now, the equal-length head-on: I die too. death_risk counts o_eff >= my_eff → equal counts. -500. Both-die vs they-kill-me — same outcome for me. ✓

Shorter snake adjacency: -5 (win_risk) + 0 (no proximity penalty since ol < my_len... I gave +2 for md==1 & shorter — encourages contesting cells near smaller snakes. Fine.)

Hmm wait, there's an issue: win_risk -5 penalty for cells a smaller snake might enter: if they enter, they die (I survive). The -5 accounts for... actually no penalty needed; maybe they avoid and no collision. But it also means they die — good for me. The -5 slightly discourages; keep small, fine. Actually, let me make it +2 bonus (their potential death is good)? Eh — the risk is that they DON'T die and instead we... no, if they enter nh, they die (I'm longer), period. It's good for me. But it's also fine if they don't. Neutral-to-good. Keep -5 (mild caution) — hmm, actually if a smaller snake will enter nh and die, nh might be their target food cell... no impact on me. Keep -5, harmless.

Now let me reconsider fw defaults vs area term balance. Typical mid-game: my_len 8, food dist 6, areas ~ 100-200. score differences: food term dominates when fw=2.2: dist 6 vs 8 → 4.4 diff. area diff: (200-120)*1.2 = 96. So area can override food — good (don't dive into pockets for food). Trap penalty: area 6 < len+2=10 → -160; food gain from dist 8→2 = 13.2 → avoids pocket. But time-aware area might rate the pocket as passable-through-tail... whatever.

Concern: fw too low early (health 100 → fw 1.4): area maximization might dominate and I wander instead of eating → length deficit vs aggressive opponents. In FFA ranking among survivors is by length; food also keeps health. Let me raise: health > 85 → fw 1.8; >50 → 2.5; >30 → 4.0; else 6.5. And safety_mode 0.8. Hmm. Eating is nearly always safe when uncontested; the food term only breaks ties among similar-area moves. fw 1.8-2.5 fine.

Actually wait — there's a subtlety: the area term min(area,220)*1.2 rewards open space up to 264 points; food term at fw 2.5 × dist ~ up to maybe 30 = 75. So area differences up to ~264 dominate food. That's intended: safety first. But it also means I'll prefer big-open-space moves over slightly-closer food. Reasonable.

But hmm, one more consideration: in FFA the biggest risk early is head-ons in food scrums; my death_risk penalty handles.

Let me also handle: what if my candidate nh is food and eating causes... eating is fine.

Also there's a subtle trap: chasing food adjacent to my own body tightly (tail stall on eat → self-collision next turn?). E.g., I eat when my length... after eating, next turn my body = [nh] + old_body (all), tail duplicated. If I'm in a tight loop, my tail stall could block my own exit → flood area computed with stall=0 for my cells... underestimate my own stall! When I'm about to eat (nh in foodset), my future body occupies MORE cells. Minor. Add: if nh in foodset, my free_times +1? Let me add stall_self = 1 if nh in foodset else 0 — but free_time is computed once, before candidates... I can compute per-candidate... too much. Approximation: add +1 stall to MY free_time globally (my_len changes... ). Simply: my stall = 1 always (slightly conservative, fine). Let me set stall: 1 for me, 2 for others. (I earlier had 0/2.)

Hmm, wait, but stall for others should maybe be more — they eat too. 2 is fine.

Let me reconsider free_time formula: t = L - i + stall. For i = L-1 (tail): t = 1 + stall. Tail cell frees next turn (after next move) — correct-ish: this turn it's already free if not dup... hmm wait. Confusion: free_time semantics = "BFS arrival time nd at which cell is passable". nd counts steps from nh. At nd=1 (next turn), which cells are free? After everyone moves again: bodies shifted. A snake's current tail cell: freed THIS turn already (not blocked if no dup). A snake's current cell b[i]: after next move, occupied unless... ugh, this is about future occupancy: after k more moves, snake occupies cells [head_k, ..., b[0], ..., b[L-1-k]] (if no eating). So cell b[i] is occupied until k > i... let me recompute: after k moves, the snake's body = [h_k, h_{k-1}, ..., h_1, b0, b1, ..., b_{L-1-k}]. So b[i] occupied while L-1-k >= i, i.e., k <= L-1-i. Free when k >= L-i. BFS arrival nd counts: nh at 0 (this turn's new head); a cell reached at nd = d means after d more of my moves from nh — which coincides with d more moves of other snakes (approximately, same turns). Cell b[i] of a snake is free when reached at time d >= L - i (its head has advanced past). So t = L - i is right, stall adds eating delay. But ALSO: this turn (d=0... nh reached at d=0), cells currently free must have t <= 0. b[i] cells have t = L-i >= 1 > 0 → blocked now ✓ (except tail: t=1 > 0 → blocked now?! But tail is FREE now if no dup!).

Bug: the tail cell b[L-1] has t = 1, but it's actually free this turn (tail retracted). And dup-tail b[-1]==b[-2]: blocked. So free_time should be: for cell b[i]: t = L - i - 1 (free when k >= L-1-i... let me recompute. After k moves, occupied cells: b[0..L-1-k] plus new heads. b[i] occupied iff i <= L-1-k iff k <= L-1-i. Free iff k >= L-i... wait: i <= L-1-k ⟺ k <= L-1-i. So b[i] free when k > L-1-i, i.e., k >= L-i. Tail: i=L-1 → free when k >= 1. But tail is free at k=0 already? No — the tail retraction happens DURING move: at k=0 (before any further move), the snake's body includes the tail... 

Hold on. Timeline: I'm evaluating MY move for this turn. All snakes move simultaneously. After this simultaneous move, tails retracted. So the "current" occupancy relevant for MY nh: tails already retracted — handled by `blocked` (exact). The flood fill explores MY FUTURE positions from nh at times d=0 (this turn, after all moves) onward. At d=0 (this turn), which cells are occupied by other snake s? Its new body: [s_newhead, b[0..L-2]] (assuming no eat). I don't know s_newhead. Cells b[0..L-2] occupied at d=0. Cell b[L-1] (tail) free at d=0. At d=1 (next turn): s's body = [s_nh2, s_nh, b[0..L-3]]... assuming no eat: occupied = b[0..L-3] ∪ new heads. Generally at time d: occupied = b[0..L-2-d] ∪ {future heads}. So b[i] occupied at time d iff i <= L-2-d, free iff d >= L-1-i. So free_time[b[i]] = L-1-i (+stall), with the exception of dup-tail (b[-1]==b[-2]): then tail didn't retract, occupied at d=0: free_time for the shared cell = min(L-1-(L-2), L-1-(L-1)) = 0?? Hmm: dup tail means body ends [.., c, c] with indices L-2, L-1 both c. At d=0: occupied = b[0..L-2] (includes both c's). At d=1: b[0..L-3]... wait with dup tail, does the NEXT move retract? The duplicated tail: after next move, one c remains... body [nh, b0..b_{L-2}] → the second c dropped, first c (index L-2) stays: occupied = b[0..L-2] at d=1?? Hmm: [.., c, c] (indices L-2, L-1). Move: head advances, tail (index L-1) drops → [nh, b0, ..., b_{L-2}] — c at index L-2 still occupied at d=1. So cell c occupied at d=0 and d=1, free at d=2. free_time = 2 = L-1-(L-2) + 1 = 1+1. So dup adds +1.

General formula: free_time[b[i]] = (L-1-i) + stall, where stall ≥ 0 for normal (0), and dup-tail cells effectively +1. Plus eating adds +1 per eat. So:

- stall_me = 1 (assume I'll eat once during the horizon — mild safety), stall_others = 2.
- For dup-tail snakes: +1 more... I can detect dup: if b[-1]==b[-2], add +1 to those cells. Eh — covered by stall margins roughly. Keep simple: stall_me=1, stall_others=2.

And `blocked` (d=0 occupancy, exact): b[0..L-2] ∪ (b[-1] if dup). Consistent with free_time: b[L-1] (tail, no dup): free_time = 0 + stall = stall ≥ 1 > 0 → but it's NOT blocked at d=0 (it's passable now!). Bug: stall makes tail cell impassable at d=0 in flood even though free. Minor conservatism in flood only (not in candidate fatality). Effect: flood area slightly underestimates when path goes through others' tails — makes me less eager to follow tails. Hmm, tail-following is a core survival trick. Let me handle precisely: set free_time[b[i]] = L-1-i+stall, but for the TAIL cell specifically when not dup, free_time = 0 (passable now). So: for i in range(L): ft = (L-1-i) + stall; if i == L-1 and not dup: ft = 0. With stall: tail=stall... no — set explicitly: tail (no dup): 0; tail (dup): 2ish. Let me just do:

```python
for i in range(L):
    c = b[i]
    if i == L-1 and not (L>=2 and b[-1]==b[-2]):
        t = 0
    else:
        t = L-1-i + stall
    ...
```

Hmm wait but for i == L-1 with dup, t = L-1-(L-1)+stall = stall; but we computed it should be 2 (occupied d=0 and d=1 → free at d=2). stall_others=2 → t=2 ✓ if I add the dup+1: t = stall + 1. Let me do: dup → t = stall + 1 for both tail cells... For i=L-2 (the other c): t = 1 + stall; free at d >= 1+stall. Correct-ish (occupied at d=0,1... it's occupied at d=1 per above analysis: at d=1 occupied = b[0..L-2] which includes index L-2). So free at d=2 → t should be 2. With stall=2: t=3 → conservative. Meh, close enough. Honestly these margins are guesswork; the key cases: (1) plain tail passable now ✓ (t=0), (2) body cells block for a while ✓.

And MY OWN cells in flood: my body cells b[i] (i≥1) — after my move, my occupied = nh + b[0..L-2]. In flood from nh at d=0: my cells b[0..L-2] occupied at d=0 → t = L-1-i + stall_me... for i=0 (my old head): occupied at d=0; frees at d=1: t=1 ✓ (formula: L-1-0+1 = L, way conservative — my old head frees at d=1 actually... wait: my body at time d (relative, after d more moves): my body = [future heads..., b0..b_{L-1-d}] hmm I'm chasing my tail through my own body: cell b0 (old head) occupied until my tail passes it: my length L → b0 occupied for L-1 more steps (until tail retracts past it) → free at d = L-1... 

Ugh wait, I conflated. Let me redo carefully. My body AFTER this turn's move: [nh, b0, b1, ..., b_{L-2}] (length L, no eat). At future step d (d more moves, no eats): my body = [h_d, ..., h_1, nh, b0, ..., b_{L-2-d}]. So b[i] (i in 0..L-2) occupied while L-2-d >= i ⟺ d <= L-2-i. Free at d >= L-1-i. So b0 free at d = L-1 ✓ (matches original formula L-i? no: L-1-i). Original I had L-i; correct is L-1-i. And nh: occupied while d <= L-1... nh free at d >= L. In flood, nh is start (seen), never re-entered — but it IS a wall for the fill until d=L... my walls_extra={nh} blocks it entirely. Slightly conservative. Fine.

For OTHER snakes (their body from THEIR perspective): same formula: their b[i] free at d >= L-1-i, where d counts their moves = my moves. Their tail b[L-1]: not occupied at d=0 at all (retracted this turn) → t=0. Their b[L-2] (current effective tail): free at d>=1. OK so:

free_time[b[i]] = L-1-i + stall, except plain tail → 0.

With stall_me=1 (my eats), stall_others=2 (their eats/uncertainty). Dup tail: both last cells +1-ish (their effective tail is b[L-2]... with dup, body after this turn: they don't drop tail next turn... let me just: if dup: t[b[L-1]] = 2 (others) — they stay; formula for i=L-1 with dup: L-1-(L-1)+stall = stall=2 ✓ automatically. And b[L-2] with dup: 1+2=3, actual 2 — conservative, fine. And non-dup tail: set 0.)

Good. Now flood_area uses free_time with the d semantics: cell passable when arrival d >= ft. nh arrival 0. ✓

Let me also double check `blocked` vs flood: blocked = currently-occupied-at-d0 = all b[0..L-2] + dup tails. flood uses free_time (≥1 for those) — consistent.

OK. Now also for the candidate fatality check I use `blocked` (exact, d=0). ✓

Now — squeeze flood for opponent: flood from their head oh... but oh is their CURRENT head; after this turn their head moved. I'm measuring their future space from their post-move position, which I approximate from oh (their head region). Better: their possible new heads = neighbors of oh; measure space from oh is an approximation that includes... eh. Standard approximation. Actually simpler: measure from oh with walls = blocked|{oh, nh}: includes their own head cell as wall (it'll be their neck — correct-ish). Their neck cell b[1]... in blocked anyway. OK.

Let me now also make sure about squeezing correctness: opp_base_area computed once per turn; per-candidate a2. Gain = base - a2 ∈ {0,1,...}. If my nh cuts a chokepoint, gain large. k=2 → score += 2*gain. With gains up to ~200 → +400 could override food terms — intended when I'm longer (aggressive cutoff). But could lure me into bad positions? Fatal/trap checks still apply. And md==1 penalties still apply. OK, cap gain contribution: min(gain, 40)*k? Cutting off 40+ cells is a real cut; capping at 40*2=80. Hmm, I'd say cap gain at 60. Let me cap: score += min(gain, 60) * squeeze_k.

Now let me write the final code cleanly.

Also handle `me` is None → return "up" via fallback chain (decide's try/except). _decide would raise on me["body"] if me None → caught → _fallback → also crashes? _fallback accesses me["body"] → me None → exception → decide catches → "up". OK but better: in _fallback guard me None → return random dir. Add.

Also: what if my health is 1? I starve this turn unless I eat. Emergency: fw 9, headon_pen 80. Fine.

Let me write out the full code now.

```python
import random
from collections import deque

DIRS = (("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0))
_valid = ("up", "down", "left", "right")

_prev_target = None


def decide(state):
    try:
        mv = _decide(state)
        if mv in _valid:
            return mv
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        pass
    return random.choice(_valid)
```

_decide:

```python
def _decide(state):
    global _prev_target
    w = state["width"]; h = state["height"]
    turn = state.get("turn", 1); maxt = state.get("max_turns", 500)
    me_id = state["you"]
    me = None; others = []
    for s in state["snakes"]:
        if s["id"] == me_id:
            me = s
        else:
            others.append(s)
    if me is None:
        return random.choice(_valid)
    my_body = [(p[0], p[1]) for p in me["body"]]
    L = len(my_body)
    head = my_body[0]
    neck = my_body[1] if L > 1 else head
    my_health = me["health"]
    foods = [(f[0], f[1]) for f in state["food"]]
    foodset = set(foods)

    blocked = set()
    free_time = {}
    for s in state["snakes"]:
        b = [(p[0], p[1]) for p in s["body"]]
        sl = len(b)
        stall = 1 if s["id"] == me_id else 2
        dup = sl >= 2 and b[-1] == b[-2]
        for i in range(sl):
            c = b[i]
            if i < sl - 1 or dup:
                blocked.add(c)
            if i == sl - 1 and not dup:
                t = 0
            else:
                t = sl - 1 - i + stall
            if c not in free_time or t < free_time[c]:
                free_time[c] = t
    # note: my head cell is in blocked (i=0 < sl-1 for sl>=2; if sl==1... spawn sl>=3)
```

Hmm wait: for sl==1?? Can't happen. But if sl==1: i==0==sl-1, not dup → blocked misses head. Guard: if sl==1: blocked.add(b[0]). Add safety: `if i < sl-1 or dup or sl == 1: blocked.add(c)`. Eh, just: blocked.add all cells where i < sl-1 or dup; plus if sl==1 add. Let me handle: for sl==1, head cell should be blocked. I'll add after loop: if sl == 1: blocked.add(b[0]).

opp_info:

```python
    opp_info = []
    for s in others:
        b = [(p[0], p[1]) for p in s["body"]]
        oh = b[0]
        on = b[1] if len(b) > 1 else (-99, -99)
        opp_info.append((oh, on, len(b)))
```

bfs_dist:

```python
    def bfs_dist(start):
        dist = {start: 0}
        dq = deque([start])
        while dq:
            x, y = dq.popleft()
            d = dist[(x, y)] + 1
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0 <= nx < w and 0 <= ny < h:
                    n = (nx, ny)
                    if n not in dist and n not in blocked:
                        dist[n] = d
                        dq.append(n)
        return dist
```

flood:

```python
    def flood(start, extra_walls):
        seen = {start}
        cnt = 1
        dq = deque([(start[0], start[1], 0)])
        while dq:
            x, y, d = dq.popleft()
            nd = d + 1
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0 <= nx < w and 0 <= ny < h:
                    c = (nx, ny)
                    if c in seen or c in extra_walls:
                        continue
                    ft = free_time.get(c)
                    if ft is not None and nd < ft:
                        continue
                    seen.add(c)
                    cnt += 1
                    dq.append((nx, ny, nd))
        return cnt
```

target selection:

```python
    dist_me = bfs_dist(head)
    dmin = None
    for f in foods:
        if f in dist_me:
            d = dist_me[f]
            if dmin is None or d < dmin:
                dmin = d
    cpen = 2 if len(opp_info) == 1 else 6
    if my_health < 30:
        cpen = 0
    best_cost = None; target = None
    for f in foods:
        if f in dist_me:
            dm = dist_me[f]
            contested = 0
            for oh, on, ol in opp_info:
                if abs(oh[0]-f[0]) + abs(oh[1]-f[1]) < dm:
                    contested = 1
                    break
            cost = dm + contested * cpen
        else:
            cost = 150 + abs(head[0]-f[0]) + abs(head[1]-f[1])
        if _prev_target is not None and _prev_target in foodset and _prev_target == f:
            cost -= 1.5   # hysteresis
        if best_cost is None or cost < best_cost:
            best_cost = cost; target = f
    _prev_target = target
```

Hmm — hysteresis: cost -= 1.5 for previous target. OK.

Wait — dmin is min over reachable foods; used for emergency. But note dmin from head; dist to target similar. OK.

field from target:

```python
    field_t = bfs_dist(target) if target is not None else None
```

emergency & weights:

```python
    turns_left = maxt - turn + 1
    safety_mode = turns_left < my_health - 4
    if safety_mode:
        fw = 0.8; hpen = 900
    elif my_health > 85:
        fw = 1.8; hpen = 500
    elif my_health > 50:
        fw = 2.5; hpen = 500
    elif my_health > 30:
        fw = 4.0; hpen = 400
    else:
        fw = 6.5; hpen = 300
    if dmin is not None and my_health <= dmin + 6:
        fw = max(fw, 8.0); hpen = min(hpen, 120)
    if my_health <= 12:
        fw = max(fw, 9.0); hpen = min(hpen, 80)
    if dmin is None and my_health < 25:
        fw = max(fw, 8.0); hpen = min(hpen, 100)
```

squeeze:

```python
    squeeze_k = 0.0
    opp_base = 0
    if len(opp_info) == 1:
        oh, on, ol = opp_info[0]
        opp_base = flood(oh, {oh})
        if not safety_mode and my_health > 35:
            if L > ol + 1:
                squeeze_k = 2.0
            else:
                squeeze_k = 0.4
```

candidates & scoring:

```python
    cands = []
    for name, dx, dy in DIRS:
        nh = (head[0]+dx, head[1]+dy)
        if nh == neck:
            continue
        if not (0 <= nh[0] < w and 0 <= nh[1] < h):
            continue
        if nh in blocked:
            continue
        cands.append((name, nh))
    if not cands:
        for name, dx, dy in DIRS:
            nh = (head[0]+dx, head[1]+dy)
            if nh == neck:
                continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h:
                return name
        return random.choice(_valid)
```

Wait — the no-cands fallback should prefer "straight". DIRS order is arbitrary; let me order preference: straight first. Compute straight first:

```python
    straight = None
    if head != neck:
        v = (head[0]-neck[0], head[1]-neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == v:
                straight = name
```

Then in no-cands: try straight first if in-bounds.

Scoring:

```python
    best_score = None; best_name = None
    for name, nh in cands:
        eating = nh in foodset
        my_eff = L + (1 if eating else 0)
        drisk = 0; wrisk = 0
        for oh, on, ol in opp_info:
            if abs(oh[0]-nh[0]) + abs(oh[1]-nh[1]) == 1 and nh != on:
                o_eff = ol + (1 if eating else 0)
                if o_eff >= my_eff:
                    drisk += 1
                else:
                    wrisk += 1
        score = 0.0
        score -= drisk * hpen
        score -= wrisk * 5
        area = flood(nh, {nh})
        if area <= L + 1:
            score -= (L + 2 - area) * 40
        score += min(area, 220) * 1.2
        if field_t is not None:
            fd = field_t.get(nh)
            if fd is None:
                fd = 60 + abs(nh[0]-target[0]) + abs(nh[1]-target[1])
        else:
            fd = 0
        score -= fd * fw
        for oh, on, ol in opp_info:
            md = abs(oh[0]-nh[0]) + abs(oh[1]-nh[1])
            if md == 1:
                if ol >= L:
                    score -= 20
                else:
                    score += 2
            elif md == 2 and ol > L:
                score -= 4
        if squeeze_k > 0:
            oh = opp_info[0][0]
            a2 = flood(oh, {oh, nh})
            score += min(opp_base - a2, 60) * squeeze_k
        if name == straight:
            score += 0.15
        score += random.random() * 0.3
        if best_score is None or score > best_score:
            best_score = score; best_name = name
    return best_name
```

Wait — there's an issue with drisk when eating at nh: if nh has food and an equal-length snake also enters, both eat (+1 each) → equal → both die → drisk. ✓ handled via o_eff/my_eff both +1.

Also: hmm, "wrisk" — when I'm longer and they enter, they die. But if they die ON nh... their body disappears; I'm fine. ✓

One more: nh == on case — nh is their neck cell → in blocked → not in cands. The `nh != on` check redundant but harmless.

Another check — food on a cell adjacent to longer snake's head, and I'm one step from it: nh = food cell; drisk counts them; -hpen (500) vs food gain (fd=0 vs alternatives fd≥1... food gain tiny: (fd_alt - 0)*fw ~ few points) + area terms. → I avoid, they take it. Correct conservative behavior.

But WAIT — there's an important scenario: what if I'M ALREADY ADJACENT to food and a LONGER snake is also adjacent, and it's my only... drisk penalty makes me orbit the food while they take it. If they're longer, that's correct (can't win the race).

Now, what if the food cell is adjacent to a longer snake's head but the food is closer to me / they're moving away? I can't know. Conservative. OK.

Also potential issue: field_t BFS from target uses `blocked` — but target food cell itself might be... food never on snake body? Food spawns on empty cells; snakes move onto food. A snake's head/body could be ON a food cell (about to eat / passed over? head on food = eats it immediately). Body on food cell: possible? Head lands on food → eaten immediately. So food cell never has body on it... except food respawned... spawns on random empty cell. And a snake head sits on food only instantaneously (eats same turn). So food cells are never in blocked. But wait — what about this: snake head moves onto food cell, eats it; another snake head also moves onto same cell same turn, both eat. Then food respawns elsewhere. So foods in state are always on empty cells ✓. So bfs_dist(target) starts from a free cell. But hmm, my OWN head adjacency: fine.

Actually — one exception: can food be under my head in state? No (eaten when landed on). OK.

Another subtle thing: `bfs_dist(head)` — head in blocked; seed fine.

Potential performance: flood called 3 + 3 (squeeze) + 1 = 7 times worst ≈ 7k expansions. Fine.

Now, the FFA case with 10 opponents: squeeze off (only when 1 other). ✓

Let me reconsider the "proximity to longer heads" penalty in FFA: with 10 snakes, many cells within md≤2 of some longer head; penalties -20/-4 per snake could accumulate heavily (~-100s) and dominate, making me flee crowds excessively... but fleeing crowds in FFA is decent survival. However, combined with food pull (fw up to ~2.5 × dist ≤ ~40) — food pull would rarely win near crowds → I'd starve-ish? No — health emergencies raise fw to 8-9 (up to dist 30 → 270) which can beat proximity penalties. So I'd eat only when hungry-ish, stay safe otherwise. That's actually a reasonable FFA profile: survival-first, moderate growth. Length still matters for final ranking among survivors... My fw when health>85 is 1.8 — vs proximity -20 per longer adjacent head. Hmm, in FFA with equal-ish lengths early (all 3), "ol >= L" true for equal → -20 near everyone. Early game everyone's equal → all cells near heads penalized → I avoid heads, take uncontested food. Good.

But late FFA when I'm the longest: no proximity penalties (ol < L mostly), I eat freely. Good.

Mid: some longer some shorter. OK, I think it's balanced enough. One tweak: in FFA maybe reduce proximity penalty to -10/-3? The head-on death_risk (-500) is the real guard; -20 is soft. Keep -20; survival bias is fine.

Let me reconsider trap penalty: `area <= L+1 → -(L+2-area)*40`. With time-aware flood, area counts eventual reachability, so a pocket behind my own tail might read fine. OK.

One more scenario — endgame FFA, 2 snakes left, I'm shorter: squeeze_k 0.4 (mild pressure), food contested cpen=2. Fine.

And 1v1 from start: both len 3. L > ol+1 never → squeeze_k 0.4 mild. Hmm, when I get longer (ate more), squeeze_k 2.0 activates → aggressive space denial. But early 1v1, priority: out-eat opponent. cpen=2 (1v1) → contest food. Good.

One more important 1v1 point: if opponent dies, I win. Encouraging risk when THEY are at low health? Skip.

Now, safety_mode check: `turns_left < my_health - 4`. my_health is current; it only decreases (unless I eat). So coasting valid if health - 1*turns_left > 0 with margin... health decreases each turn; after turns_left turns, health = my_health - turns_left + (eats). If my_health - turns_left >= 5, I survive to the end without food. Condition: turns_left < my_health - 5. I wrote -4; use -5. Also should compare death-time ranking: if others will die before end... unknowable. OK.

Wait, one more: in safety_mode, hpen=900 — but if a snake is longer and chases me into a corner... standard play. Fine.

Also in safety_mode, if another survivor is LONGER than me and also coasting, they outrank me — I should still try to grow if free. fw 0.8 takes free food. Also maybe don't enter full safety if I'm not the longest? If the longest other snake is likely to survive too, length decides → I should keep eating at moderate risk. Refine: safety_mode = turns_left < my_health - 5 AND (my_len >= max other len) — if I'm longest, coast; if not, keep fw at ~2 and hpen 700 (safer than normal but still eat). Let me implement: 

```python
    max_olen = max((ol for _,_,ol in opp_info), default=0)
    can_coast = turns_left < my_health - 5
    if can_coast and L >= max_olen:
        safety_mode → fw=0.8, hpen=900
    elif can_coast:
        fw = max(fw, 1.6)? 
```

Hmm, keep simple: if can_coast and L >= max_olen: fw=0.8, hpen=900. Else if can_coast: fw=2.0, hpen=650. OK.

Now think about whether the food-chasing BFS (field_t) handles "food might be eaten before I arrive" — target food could be eaten by another snake mid-route → then I wasted distance, and _prev_target resets next turn. Acceptable.

Another rule-check: food respawn happens when eaten — "被吃掉的食物在随机空格重新出现". So food count constant. I use current foods only. ✓

Now — one more critical review of the head-on risk: I only consider snakes whose head is manhattan-1 from nh. But what about a longer snake whose head is at distance 2 that could... they can't reach nh this turn. ✓. And what about nh being where a longer snake's TAIL... no, tail isn't a head.

What about mutual head-on where BOTH of us avoid → both fine. ✓

What about a longer snake entering the cell my head currently occupies (they eat my head cell)? My head vacates; their head enters my old head cell — no interaction (different cells post-move: my nh vs their nh=my old head). No collision (my old head cell is my neck — body collision for THEM! They'd die hitting my neck... wait their head enters my old head cell = now my neck = my body → THEY die by body collision). So snakes entering my current head cell die (unless my neck frees... my neck is b[1], occupied while... this turn it's my 2nd segment — body collision for them). Interesting: no risk to me. ✓ Not modeled (their problem).

What about them entering my neck-adjacent... whatever.

OK — also verify candidate filter for "nh == neck": if head == neck (stacked), nh (neighbor of head) ≠ neck==head → all 4 pass. ✓. When L==2? Can't happen (start 3, only grow). If body length could be... never shrinks. min 3. OK but code guards anyway (L>1 checks).

Wait, actually — the dup-tail representation: body [..., c, c] with the last two equal. My neck = body[1]. All good.

Let me also double check flood start: nh might be in free_time?? nh not in blocked; free_time cells ⊆... free_time includes tail cells with t=0 — tail cells are NOT in blocked (when not dup) but ARE in free_time with t=0. nh could be a tail cell (t=0, passable at d=0 — start at d=0: fine, it's passable since t=0 ≤ 0). The flood function doesn't check start's free_time — correct since we filter nh ∉ blocked, and tail cells are legal starts. ✓

But in flood, the START nh being another snake's tail cell: as their body persists, nh occupied... I'm ON it after moving; they move on. The fill from nh at d=0 — nh in extra_walls so not re-entered. ✓

Now the squeeze flood: flood(oh, {oh}) — oh is in blocked; start allowed (I removed blocked-start check). Fine.

Edge: flood start on food? Fine.

Let me also reconsider: `field_t.get(nh)` — if nh not in field (different component or blocked path), fd = 60 + manhattan — strong deterrent (60*fw ≥ 108). That's intended: prefer candidates with a real path to target. But early game when target is across the board, most candidates have finite fd ~ similar values. ✓

One more potential flaw: field_t computed from target with CURRENT blocked — as bodies move, paths open. Candidates blocked from target now get 60+manhattan even if actually fine next turn. Acceptable.

Also `fd = 0 if field_t is None` — no target (no food? impossible since food count = snakes+1 ≥ 2... but if foods list empty somehow, target None). Fine.

I think there might be one more consideration: opening move at turn 1 with stacked body — flood areas all similar; food pull decides; fine.

Also — hmm, `_prev_target` global persists across turns ✓ (module reload per game ✓).

Let me also double-check `decide` returns only valid strings. _decide returns best_name from DIRS names ✓; cands-empty branch returns name from DIRS ✓; random.choice(_valid) ✓.

Let me reconsider the time-aware flood correctness once more with a concrete case: my body [H(0), b1, b2, T(3)], L=4, no dup. blocked = {H, b1, b2}. free_time: H: 4-1-0+1=4; b1: 3+1=4? wait: sl-1-i+stall = 4-1-1+1 = 3; b2: 4-1-2+1=2; T: 0. Hmm: b2 (index 2): after this turn my body = [nh,H,b1,b2]; b2 occupied at d=0; at d=1: [.., nh, H, b1] wait L=4: body at d=1 = [h2, h1, nh, H] — hmm that's if I keep moving: at d=1, body = [h2, h1, nh, H, b1]? No: length 4 constant: at d=1 body = [h2, h1, nh, H]. So b1 free at d=1?? Let me recount: this turn (d=0): body = [nh, H, b1, b2]. d=1: [nh2, nh, H, b1]. d=2: [nh3, nh2, nh, H]. So H free at d=3, b1 free at d=2, b2 free at d=1, T free at d=0... but formula gave H:4, b1:3, b2:2, T:0. Formula is +1 conservative for me (stall=1 accounts for eating). Without stall: H:3 ✓, b1:2 ✓, b2:1 ✓, T:0... formula sl-1-i: H:3 ✓. With stall=1 → +1. So stall=1 for me models one eat during the horizon. Good, intended.

For others, stall=2 models up to 2 eats — maybe too conservative? If other snake doesn't eat, their cells free 2 turns earlier than modeled → I underestimate my space near them → avoid tight tail-following of well-fed snakes. Reasonable safety bias. Keep.

Hmm, actually, wait: is it TOO conservative in a common scenario — me following directly behind a longer snake's tail through a corridor? free_time of their tail = 0 (exact), their b[L-2] = 1+2=3 (actual 1). If corridor is narrow (their body fills it), my flood counts their body cells as opening at stall-delayed times — still opens eventually, area counts eventually-reachable cells. Area is total count, not timed. So corridor reads passable. ✓ Time-aware area counts eventual reachability — conservative delays only affect whether reachable at all (rarely). Good.

Now — one more thing: the `area` measure counts all eventually-reachable cells; a huge area behind a long snake's body through their tail... fine.

Also `min(area, 220)` — on 31x31 (961 cells), most mid-game areas >> 220 → area term saturates → food/risk decide. On 15x15 (225), saturates too. So area term mostly matters in tight spots. Hmm, that reduces the "prefer open space" guidance in open play. Maybe cap at 400 for 31x31? Weight 1.2*400=480 vs food 2.5*dist... Let me scale cap by board: cap = w*h // 3 (15x15→75, 31x31→320). 15x15: min(area,75)*1.2 ≤ 90 — food fw 2.5*dist... balanced-ish. Let me use cap = (w*h)//3 + 10. OK.

Also the trap threshold `area <= L+1` — with time-aware area, a survivable tail-chase loop reads area ≥ ~L. Threshold fine.

Now, let me reconsider drisk for the EQUAL-length case in 1v1 specifically — equal length, contested food: I always yield → opponent (if aggressive) eats everything → they outgrow me → then they dominate. Hmm. In 1v1, yielding every contested food to an equal-length opponent is losing strategy vs aggressive bots. But many opponents will also be conservative → mutual yield → food sits. With cpen=2 I still contest (approach) contested food in 1v1; at the final adjacency, drisk -500 makes me yield... unless I got there first by 1 turn (then THEY yield if conservative; if they don't, if we're equal, we both die). 

Improvement: in 1v1, if I arrive at the food cell and an equal-length opponent is also adjacent — the outcome depends on whether they enter. Conservative bots won't. Aggressive will (both die). Since both-die is a LOSS for me (rank tie? both die same turn, same length → tie... in Bradley-Terry that's ~0.5). Yielding food = I get less length but likely both survive to 500 → ranked by length → I lose if I keep yielding. Both-die = tie. Yielding = lose-by-length. So actually gambling (entering) is BETTER than yielding, if the alternative is losing the length race?! Unless I can find other food. My cpen=2 only mildly avoids contested food; when uncontested food exists, I take it. When ALL food is contested (1v1, 3 foods, opponent contests all — unlikely all 3).

Let me add: in 1v1 (exactly 1 opponent alive), reduce equal-length head-on penalty somewhat (they're likely also conservative → they yield; if they don't, tie). hpen for equal: maybe 250 in 1v1? vs longer: keep 500+. Let me differentiate: drisk split into drisk_longer and drisk_equal. In 1v1: equal penalty = 200; longer = 500+. In FFA: equal = 500 (both die while others benefit — worse in FFA). Yes, in FFA mutual death is terrible (others rank above). In 1v1, mutual death = tie ≈ average, and yields food-race benefits when they yield. Actually if they yield I get food AND survival. Expected value strongly favors entering when 1v1 & equal length... unless they're aggressive. Mixed: penalty 150 in 1v1 equal case? Let me think: if I enter and they yield: +food. If both enter: tie (0). If I yield: -length deficit. Entering is clearly better unless they always enter. With penalty 150 vs food gain ~ (fd diff)*fw ~ small... hmm, the decision at the final step: candidate A = food cell (drisk_equal=1, -150), fd=0; candidate B = safe cell, fd=1 or 2. Score A = -150 + 0 + area stuff; B = -fd*fw + ... A loses by ~145. So I still yield! The food-gain term is tiny (fd 0 vs 1). To actually contest, equal-penalty in 1v1 must be < ~5. That's basically always gambling on contested food. Too aggressive? If opponent is aggressive too → we both die turn 30 → tie. If opponent conservative → I win length race. Hmm, in a field of strong opponents, many are conservative (survival-first). But mutual annihilation against aggressive ones gives ties (0.5), yielding to them gives losses... 

Actually wait — yielding isn't a loss necessarily: I can find OTHER food. The contested-food gamble matters only when food is scarce. There are 3 foods in 1v1 (15x15). If I always yield contested ones, I still eat the uncontested ones. Opponent can't contest all 3 (unless longer and camping... they eat one at a time). So yielding contested food in 1v1 costs a little growth, not the game. Balanced approach: moderate penalty for equal in 1v1, like 120. Then at the final approach step, food cell scores -120 vs safe alternative -1*fw(2.5)+... → still yield. Hmm.

OK here's the thing: the decision point is when BOTH heads are adjacent to the food. Before that, we approach. If I'm 1 step closer, I enter food when they're 2 away — no risk at all. The gamble only arises at simultaneous-adjacency. With cpen=2 target selection, I mildly prefer the less-contested food, so simultaneous-adjacency at the same food is somewhat avoided. When it happens, yielding costs me a bit; gambling risks a tie. I'll set equal-length penalty in 1v1 to 140, longer to 520. It biases toward yielding while allowing override when the alternative is bad (trap/starve). Fine — actually you know, let me go a bit lower: 100. The alternative-safe-move usually wins by only ~10-20 points from fd/area terms, so 100 still yields. To make gambling happen I'd need <10. I'll keep yielding vs equal (safe) — top bots likely also avoid mutual death; the length race is then decided by target selection efficiency and safer stealing (arrive first). Also arriving first happens when I take better routes. OK.

Hmm, but one more 1v1 dynamic: if opponent is LONGER and contests food aggressively, I can never eat contested food → I starve? No: 3 foods; they can't camp all. And if I starve to low health, emergency mode lowers hpen to ~80-120 → I'd gamble with starvation imminent. Reasonable.

Now FFA equal-length: mutual death in FFA is very bad (others gain rank). Keep 500.

Also longer-snake penalty in 1v1: they survive, I die → -500 (or 900 safety). ✓

Implementation: 

```python
        eq_pen = 140 if len(opp_info) == 1 else 500
        ...
        for oh, on, ol in opp_info:
            if adjacent and nh != on:
                o_eff = ol + (1 if eating else 0)
                if o_eff > my_eff:
                    drisk += 1
                elif o_eff == my_eff:
                    erisk += 1
                else:
                    wrisk += 1
        score -= drisk * hpen   # longer/equal... 
```

Hmm wait, I need to separate: drisk (they kill me) vs erisk (both die). hpen for drisk (they're strictly longer after food adjustments); erisk gets eq_pen. But hpen itself varies with emergency (down to 80). erisk: also lower in emergency? If starving, both-die beats starving → erisk min scaled too: erisk_pen = min(eq_pen, hpen). Let me just use: score -= drisk*hpen + erisk*min(eq_pen, hpen) ... simpler: use hpen for both but hpen = min(hpen, eq_pen) when only erisk? Overcomplicating. Just: pen_i = hpen if o_eff > my_eff else min(eq_pen, hpen). Sum. Fine:

```python
        risk_pen = 0
        for ...:
            if adjacent...:
                if o_eff > my_eff: risk_pen += hpen
                elif o_eff == my_eff: risk_pen += min(eq_pen, hpen)
                else: risk_pen += 5
```

Wait for equal with eating nuance: if nh has food, both +1 → equal stays equal. If nh no food, equal stays. o_eff==my_eff ⟺ ol==L. ✓. o_eff > my_eff ⟺ ol > L... wait: o_eff = ol + eat, my_eff = L + eat, same eat flag (food at nh) → comparison ⟺ ol vs L. So eating doesn't change comparisons. Simplify: compare ol vs L directly. ✓ (Since both would eat the same food if both heads there.) Nice: o_eff irrelevant.

Hmm wait — careful: if nh has food and THEY enter nh, they eat (their head on food). If they DON'T enter nh, nobody eats that food. My my_eff only matters if they enter. So comparison ol vs L. ✓

So:

```python
        for oh, on, ol in opp_info:
            if abs(oh[0]-nh[0])+abs(oh[1]-nh[1]) == 1 and nh != on:
                if ol > L:
                    risk_pen += hpen
                elif ol == L:
                    risk_pen += min(eq_pen, hpen)
                else:
                    risk_pen += 4
```

Good, simpler.

Now — one more thing to verify: `nh != on` — on is their neck; if nh == on, nh in blocked → filtered already. on is (-99,-99) if missing — never equals nh. ✓ redundant but safe.

Now the food-denial consideration in 1v1: my eating also denies them. Already reflected in eq behavior? Not really. Skip.

Next: consider adding a small bonus for eating (growth): when nh in foodset: score += 3? The fd=0 vs 1 already rewards. Fine.

Potential issue — target food unreachable via field (fd = 60+man) for ALL candidates (e.g., target across a wall of bodies): all get similar 60+man, differentiation by manhattan. OK.

Let me now also think about pathological oscillation: two equal candidates with jitter ±0.3 and straight bonus 0.15 — stable enough.

Health-based retriggering: as health decays through thresholds, fw jumps (1.8→2.5) — smooth enough.

Now — the FIRST-turn time limit is 1s; everything fast. The per-turn 50ms — fine.

Let me also consider: what if `state["snakes"]` contains snakes with empty body? Guard: skip snakes with len(body)==0? They wouldn't be alive. Add filter.

What about me["body"] length 1? Guard L==1: neck = head; blocked: my head cell should be blocked... my code: sl==1: loop i=0: i < sl-1 false, dup false (needs sl>=2) → not blocked! Bug. Add: if sl == 1: blocked.add(b[0]); free_time[b[0]] = big. Actually free_time formula for sl==1: t = sl-1-0+stall = stall. Meh. Since this shouldn't happen, add minimal guard: treat sl==1 as blocked cell with free_time = 3. I'll code: 

```python
        for i in range(sl):
            c = b[i]
            dup = sl >= 2 and b[-1] == b[-2]
            if i < sl - 1 or dup or sl == 1:
                blocked.add(c)
            if sl == 1:
                t = 3
            elif i == sl - 1 and not dup:
                t = 0
            else:
                t = sl - 1 - i + stall
```

OK. Also possible: body with length 2? Then neck exists; fine.

Now — hmm, one more strategic consideration for FFA ranking: "活到最后的排在所有死蛇前面，活着的之间也比长度". If I'm likely to be among survivors, length matters; if likely to die mid-pack, survival rank matters more. My bot is survival-first — good for FFA (many aggressive bots die). 

One more: when others die around me, food count = initial snakes + 1? "场上始终保持"蛇的条数 + 1"颗食物（单挑 3 颗，大乱斗 12 颗）" — "蛇的条数" likely = initial count? "单挑 3 颗，大乱斗 12 颗" = num_snakes+1 with num_snakes = initial (2→3, 11→12). So constant 12 in FFA even as snakes die. Fine, doesn't matter.

Now write _fallback properly with straight preference:

```python
def _fallback(state):
    w = state["width"]; h = state["height"]
    me = None
    for s in state["snakes"]:
        if s["id"] == state["you"]:
            me = s
            break
    if me is None or not me["body"]:
        return random.choice(_valid)
    body = [(p[0], p[1]) for p in me["body"]]
    head = body[0]
    neck = body[1] if len(body) > 1 else (-99, -99)
    blocked = set(body[:-1])
    if len(body) >= 2 and body[-1] == body[-2]:
        blocked.add(body[-1])
    straight = None
    if head != neck:
        v = (head[0]-neck[0], head[1]-neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == v:
                straight = name
                break
    order = [d for d in DIRS]
    if straight:
        # put straight first
        order.sort(key=lambda d: d[0] != straight)
    for name, dx, dy in order:
        nh = (head[0]+dx, head[1]+dy)
        if nh == neck:
            continue
        if 0 <= nh[0] < w and 0 <= nh[1] < h and nh not in blocked:
            return name
    for name, dx, dy in order:
        nh = (head[0]+dx, head[1]+dy)
        if nh == neck:
            continue
        if 0 <= nh[0] < w and 0 <= nh[1] < h:
            return name
    return random.choice(_valid)
```

Wait: blocked = set(body[:-1]) includes my head — moving into own head cell impossible anyway (not adjacent... head isn't adjacent to itself; neighbors only). Includes neck ✓.

Now assemble everything. Also reconsider: should `flood` count the start cell in area? cnt starts 1. Trap check `area <= L+1` — includes start. Fine.

One more thought on `bfs_dist` for field_t: it ignores time-freeing (static walls). A target behind my own long body: field says unreachable though I could tail-follow. fd=60+man keeps mild pull. Then when path opens (tail moves), field updates. Acceptable.

Actually, let me improve slightly: run field BFS with... no, keep static. Fine.

Double-check global mutable state and idempotence: _prev_target only. ✓

Now, potential issue: `random` is pre-seeded by judge; using random.random() for jitter — deterministic per seed, fine.

Final review of the scoring balance in a NORMAL mid-game 1v1 turn: my_len 9, health 80, target dist ~7. Candidates: 3 moves, areas maybe 150 (15x15 = 225 total minus bodies). area term: min(150, 75)*1.2 = 90 vs min(140,75)*1.2 = 90 (capped) — saturates at cap 75*1.2=90 → area differences only below cap. Hmm, cap w*h//3+10 = 85 → min(area,85)*1.2. Areas 150 vs 140 both → 85 → equal. Good: area only matters when small. But then what guides me toward open space generally? Food term mostly. That's fine — food pulls through open space naturally.

Hmm, but wait: is preferring-food-always OK when health full? fw 1.8 — mild. Yes.

Now, trap check: area <= L+1 → penalty. With cap at 85, mid-size pockets (say 40 when L=9) get min(40,85)*1.2=48 vs open 85*1.2=102 → 54 diff — decent gradient toward open space below cap. ✓

Edge case: what if my length grows huge (L=60) on 15x15? L+1=61; pockets < 62 penalized (L+2-area)*40 — strong. Time-aware area helps evaluate tail-chase survival. OK.

Now — I want to double check the drisk interplay with squeeze aggression: squeeze flood from opp head with walls {oh, nh} — the gain counts cells denied. If nh is adjacent to their head (risk cell), squeeze gain could be big (blocking their exits) — combined with -hpen... hpen 500 vs gain 60*2=120 → risk dominates. ✓

Let me also sanity check we handle "opponent adjacent to my head but not to nh" — no risk from them entering nh (they're 2 away). ✓

I also want a tiny aggression: eating food NEAR a shorter snake to deny them — wrisk +... wrisk penalty -4 discourages contesting vs shorter. Since vs shorter I WIN head-ons, contesting is good for me. Remove wrisk penalty → make it 0? If they enter, they die — good. But it also kills them → fewer snakes (FFA: fine). Set wrisk penalty to 0 and rely on proximity bonus +2. OK, set to 0... hmm, one caveat: vs shorter snake entering nh — CERTAIN for them only if they actually enter; if they don't, no effect. No downside for me either way. Penalty 0. But there's an edge: nh on food, shorter snake enters: both eat; they die; I keep... they ate too (health 100 before dying) — irrelevant, they're dead. I gain length + they die. Pure win. Penalty 0. 

Now — let me reconsider one thing in target selection: foods occupied... nah done.

Also — should proximity penalty apply for md==1 & ol >= L even when nh is not enterable by them (nh == on)? nh==on is blocked → not a candidate. ✓

What about md==1 with ol >= L but they're boxed in / their only move is elsewhere — unknowable. Keep penalty.

Let me also think: do I need to worry about my OWN neck-reverse... filtered. ✓

What if straight is None (head==neck)? fine.

Potential bug: `order.sort(key=lambda d: d[0] != straight)` — d[0] is name; comparing name != straight (a name) ✓.

Also in _decide no-cands branch, prefer straight:

```python
    if not cands:
        pref = [straight] if straight else []
        for name, dx, dy in DIRS:
            if name != straight:
                pref.append(name)
        for name in pref:
            for dn, dx, dy in DIRS:
                if dn == name:
                    nh = (head[0]+dx, head[1]+dy)
                    if nh != neck and 0 <= nh[0] < w and 0 <= nh[1] < h:
                        return name
        return random.choice(_valid)
```

Simpler:

```python
    if not cands:
        names = [straight] if straight else []
        names += [n for n, _, _ in DIRS if n != straight]
        for n in names:
            for dn, dx, dy in DIRS:
                if dn == n:
                    nh = (head[0]+dx, head[1]+dy)
                    if nh != neck and 0 <= nh[0] < w and 0 <= nh[1] < h:
                        return n
        return random.choice(_valid)
```

OK. Now full code assembly. Let me write it completely and carefully review.

```python
import random
from collections import deque

DIRS = (("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0))
VALID = ("up", "down", "left", "right")

_prev_target = None


def decide(state):
    try:
        mv = _decide(state)
        if mv in VALID:
            return mv
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        pass
    return random.choice(VALID)


def _decide(state):
    global _prev_target
    w = state["width"]; h = state["height"]
    turn = state.get("turn", 1)
    maxt = state.get("max_turns", 500)
    me_id = state["you"]
    me = None
    others = []
    for s in state["snakes"]:
        if not s.get("body"):
            continue
        if s["id"] == me_id:
            me = s
        else:
            others.append(s)
    if me is None:
        return random.choice(VALID)

    my_body = [(p[0], p[1]) for p in me["body"]]
    L = len(my_body)
    head = my_body[0]
    neck = my_body[1] if L > 1 else (-99, -99)
    my_health = me["health"]
    foods = [(f[0], f[1]) for f in state["food"]]
    foodset = set(foods)

    # ---- occupancy model ----
    blocked = set()   # cells fatal to enter THIS turn
    free_time = {}    # cell -> earliest flood-arrival step at which passable
    for s in state["snakes"]:
        b = [(p[0], p[1]) for p in s["body"]]
        if not b:
            continue
        sl = len(b)
        stall = 1 if s["id"] == me_id else 2
        dup = sl >= 2 and b[-1] == b[-2]
        for i in range(sl):
            c = b[i]
            if i < sl - 1 or dup or sl == 1:
                blocked.add(c)
            if sl == 1:
                t = 3
            elif i == sl - 1 and not dup:
                t = 0
            else:
                t = sl - 1 - i + stall
            if c not in free_time or t < free_time[c]:
                free_time[c] = t

    opp_info = []
    for s in others:
        b = [(p[0], p[1]) for p in s["body"]]
        oh = b[0]
        on = b[1] if len(b) > 1 else (-99, -99)
        opp_info.append((oh, on, len(b)))
    n_opp = len(opp_info)

    # ---- helpers ----
    def bfs_dist(start):
        dist = {start: 0}
        dq = deque([(start[0], start[1])])
        while dq:
            x, y = dq.popleft()
            d = dist[(x, y)] + 1
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= nx < w and 0 <= ny < h:
                    n = (nx, ny)
                    if n not in dist and n not in blocked:
                        dist[n] = d
                        dq.append((nx, ny))
        return dist

    def flood(start, extra_walls):
        seen = {start}
        cnt = 1
        dq = deque([(start[0], start[1], 0)])
        while dq:
            x, y, d = dq.popleft()
            nd = d + 1
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= nx < w and 0 <= ny < h:
                    c = (nx, ny)
                    if c in seen or c in extra_walls:
                        continue
                    ft = free_time.get(c)
                    if ft is not None and nd < ft:
                        continue
                    seen.add(c)
                    cnt += 1
                    dq.append((nx, ny, nd))
        return cnt

    # ---- target food ----
    dist_me = bfs_dist(head)
    dmin = None
    for f in foods:
        if f in dist_me:
            if dmin is None or dist_me[f] < dmin:
                dmin = dist_me[f]

    cpen = 2 if n_opp == 1 else 6
    if my_health < 30:
        cpen = 0
    target = None
    best_cost = None
    for f in foods:
        if f in dist_me:
            dm = dist_me[f]
            contested = 0
            for oh, _on, _ol in opp_info:
                if abs(oh[0]-f[0]) + abs(oh[1]-f[1]) < dm:
                    contested = 1
                    break
            cost = dm + contested * cpen
        else:
            cost = 150 + abs(head[0]-f[0]) + abs(head[1]-f[1])
        if f == _prev_target:
            cost -= 1.5
        if best_cost is None or cost < best_cost:
            best_cost = cost
            target = f
    _prev_target = target
    field_t = bfs_dist(target) if target is not None else None

    # ---- weights ----
    turns_left = maxt - turn + 1
    max_olen = 0
    for _oh, _on, ol in opp_info:
        if ol > max_olen:
            max_olen = ol
    can_coast = turns_left < my_health - 5
    if can_coast and L >= max_olen:
        fw = 0.8; hpen = 900
    elif can_coast:
        fw = 2.0; hpen = 650
    elif my_health > 85:
        fw = 1.8; hpen = 500
    elif my_health > 50:
        fw = 2.5; hpen = 500
    elif my_health > 30:
        fw = 4.0; hpen = 420
    else:
        fw = 6.5; hpen = 320
    eq_pen = 140 if n_opp == 1 else 500
    if dmin is not None and my_health <= dmin + 6:
        fw = max(fw, 8.0); hpen = min(hpen, 120); eq_pen = min(eq_pen, 100)
    if my_health <= 12:
        fw = max(fw, 9.0); hpen = min(hpen, 80); eq_pen = min(eq_pen, 60)
    if dmin is None and my_health < 25:
        fw = max(fw, 8.0); hpen = min(hpen, 100); eq_pen = min(eq_pen, 80)

    area_cap = (w * h) // 3 + 10

    # ---- squeeze (1 opponent) ----
    squeeze_k = 0.0
    opp_head = None
    opp_base = 0
    if n_opp == 1:
        opp_head = opp_info[0][0]
        opp_len = opp_info[0][2]
        opp_base = flood(opp_head, {opp_head})
        if not can_coast and my_health > 35:
            squeeze_k = 2.0 if L > opp_len + 1 else 0.4

    # ---- candidates ----
    straight = None
    if L > 1 and head != neck:
        v = (head[0]-neck[0], head[1]-neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == v:
                straight = name
                break

    cands = []
    for name, dx, dy in DIRS:
        nh = (head[0]+dx, head[1]+dy)
        if nh == neck:
            continue
        if not (0 <= nh[0] < w and 0 <= nh[1] < h):
            continue
        if nh in blocked:
            continue
        cands.append((name, nh))

    if not cands:
        names = [straight] if straight else []
        names += [n for n, _, _ in DIRS if n != straight]
        for n in names:
            for dn, dx, dy in DIRS:
                if dn == n:
                    nh = (head[0]+dx, head[1]+dy)
                    if nh != neck and 0 <= nh[0] < w and 0 <= nh[1] < h:
                        return n
        return random.choice(VALID)

    best_score = None
    best_name = None
    for name, nh in cands:
        score = 0.0
        # head-on risk
        for oh, on, ol in opp_info:
            if abs(oh[0]-nh[0]) + abs(oh[1]-nh[1]) == 1 and nh != on:
                if ol > L:
                    score -= hpen
                elif ol == L:
                    score -= min(eq_pen, hpen)
                # shorter: they die, no penalty
        # space
        area = flood(nh, {nh})
        if area <= L + 1:
            score -= (L + 2 - area) * 40.0
        score += min(area, area_cap) * 1.2
        # food
        if field_t is not None:
            fd = field_t.get(nh)
            if fd is None:
                fd = 60 + abs(nh[0]-target[0]) + abs(nh[1]-target[1])
            score -= fd * fw
        # proximity to bigger heads
        for oh, on, ol in opp_info:
            md = abs(oh[0]-nh[0]) + abs(oh[1]-nh[1])
            if md == 1:
                if ol >= L:
                    score -= 20.0
                else:
                    score += 2.0
            elif md == 2 and ol > L:
                score -= 4.0
        # squeeze
        if squeeze_k > 0:
            a2 = flood(opp_head, {opp_head, nh})
            gain = opp_base - a2
            if gain > 0:
                score += min(gain, 60) * squeeze_k
        if name == straight:
            score += 0.15
        score += random.random() * 0.3
        if best_score is None or score > best_score:
            best_score = score
            best_name = name
    return best_name
```

Wait — the proximity md==1 penalty of -20 duplicates the head-on penalty (adjacent = enterable). For ol > L: total -(hpen+20). OK intended.

Hmm — also, cells adjacent to a longer snake's head where their entering is impossible because... nh != on checked only; their entering also impossible if nh is their... no other case. Fine.

Bug check: in the no-cands branch: `if nh != neck` — neck could be (-99,-99) fine.

Another check: `field_t.get(nh)` — field_t was BFS from target with blocked walls. nh adjacent to head; nh could equal target (fd... dist[target]=0? bfs_dist(target): dist={target:0}; nh==target → fd=0 ✓).

Wait, bfs_dist(target): target must not be in blocked — foods never on bodies ✓ (argued earlier). But careful: could food be on a cell that a snake's body occupies... let me re-verify: food spawns on "随机空格" (empty cell). Snake eats when head lands on food. So no body-on-food states persist. ✓

Also potential: two foods same cell? No.

Now — think about whether flood for area should include "nh in extra_walls" — I pass {nh}: prevents counting nh (it's my head — occupied). But cells reachable THROUGH nh later (nh frees after my body passes)? nh stays my neck next turn etc. — my head cells remain occupied L turns. extra_walls blocks nh entirely — slightly conservative ✓.

One more: flood counts cells including ones that other snakes' heads will occupy/claim. Overestimate. Accept.

Let me trace a simple scenario to sanity check: 1v1, turn 1. Both len 3 stacked, me at (3,3), opp at (11,11), 15x15, 3 foods. blocked = {(3,3), (11,11)} + tails dup → same cells. free_time: (3,3): i=2 dup → t = sl-1-i+stall = 3-1-2+1=1; min over i=0,1,2: i=0: 3-1-0+1=3; i=1: 2; i=2 dup → 1+... wait for dup tail I set t = sl-1-i+stall for i=sl-1 too? Code: `elif i == sl-1 and not dup: t=0 else: t = sl-1-i+stall`. For i=2, dup: t = 3-1-2+1 = 1. Hmm earlier analysis said dup tail occupied at d=0 and d=1, free at 2 → should be 2. stall_me=1 gives 1 — optimistic by 1. Whatever, margins.

Candidates from (3,3): up (3,2), down (3,4), left (2,3), right (4,3) — all free. dist_me from head... fine. Target food: contested if opp manhattan < my dist — opp at (11,11) far → foods near me uncontested. field_t, flood areas all ~200 → capped 85. fd differences decide + jitter. Reasonable: moves toward target. ✓

Another trace: near-wall. head (0,5), candidates left → (-1,5) out → excluded ✓.

Trace risk: opp longer, adjacent scenario. Suppose opp head (5,5) len 10, my head (5,3) len 6, nh candidates (5,4) [between us, distance 1 from opp head] → ol > L → score -= 500+20; other candidates fine. I avoid. ✓

Now, one more thought about `hpen` in emergencies being 80: a longer snake adjacent — I might gamble through them when starving. If certain starvation vs 50-80% death... reasonable.

Potential issue: emergency mode with hpen=120 and ALL candidates risky → pick least bad (max score still chosen; fatal ones excluded since blocked filter is exact). ✓

Now — timing worry: `flood` in squeeze loop: for each candidate, full flood from opp head ~ up to 961 cells → 3 extra floods — fine.

Python version 3.13 — all standard.

One more thing: `_prev_target` compares tuple equality — foods are tuples ✓ (I convert). 

Also the hysteresis cost -= 1.5 even if unreachable (cost 150+man) — fine.

Edge: foods empty (shouldn't happen): target None, field_t None → food term skipped. dmin None. OK.

Now — let me reconsider one potential flaw: **the `blocked` set includes OTHER snakes' head cells**. Suppose opponent head is adjacent to my head and all my candidate cells are: their head cell (blocked — correct, fatal), or other cells. Fine.

But here's a subtle FFA situation: a SHORTER snake's head adjacent to my nh — I get +2 (proximity) and no risk penalty. If they enter nh, they die. But careful — is that right? nh entered by both heads: they die (shorter), I live. But ALSO: could their DEATH... they vanish; no effect. ✓ And if nh is food, both eat, they die, I keep length. ✓

Another subtle case: nh adjacent to an equal-length snake's head — I avoid (eq_pen 500 FFA). But what if that equal snake is ABOUT to die (health 1, no food)? Unknown; conservative fine.

Now think about failure mode: my bot boxed by two longer snakes; all candidates risky (-500 each); pick max by other terms. OK.

Another failure mode: flood overestimation in a pocket shared with a longer snake entering — I die to head-on... covered by risk penalty only when heads adjacent at decision time. Deeper overlaps: risk materializes later turns as we co-fill a region; each turn I re-evaluate and dodge. Generally OK.

I think the bot is solid. Let me also double check the "dup" detection for MY body when I just ate: my body [..., c, c]. My tail cell = c stays blocked ✓ so I can't reverse into my tail this turn. free_time of c: min(sl-1-(L-1)+stall, sl-1-(L-2)+stall) = min(1, 2) = 1 (stall=1) — actual: occupied at d=0 and d=1 (next turn tail doesn't move... wait, after eating this turn, next turn tail DOES move (the dup resolves). Hmm: body [.., c, c] at turn t. Turn t+1: move → [nh, ..., c] — one c remains, so c occupied at d=1, free at d=2. free_time=1 is optimistic by 1. Meh.

Now, potential subtle bug: `bfs_dist` treats `blocked` as walls — including FOOD? Foods not blocked ✓.

Also: `bfs_dist(head)` — my head in blocked, seeds dist 0, expands neighbors not blocked ✓.

Also field_t BFS from target: what if target adjacent to my head — dist includes nh ✓.

What about candidate fd when field_t[nh] exists but huge (long way around) — fd*fw big → avoided. ✓

I realize there might be an issue with target hysteresis when target food gets eaten by someone else: _prev_target cell now empty (food respawned elsewhere) → next turn f != _prev_target for all → new target. ✓

Let me also add a small global: _last_resort? Not needed.

Let me now think about whether to add "avoid cells adjacent to where two heads could both arrive"... skip.

One more important scenario: FFA early — 11 snakes ring on 31x31. Snakes spaced ~ (perimeter ~120 / 11 ≈ 11 cells apart). Foods random. My bot picks nearest uncontested food. Should be fine.

Potential problem: all 11 bots (including mine) rush center foods → scrums → my conservative penalties make me yield and find edge food. Good for survival.

Also the initial stacked bodies: blocked = single cell per snake. flood from any nh: free_time of that spawn cell = 1 → passes at nd>=1 → area large. ✓

Alright — one more optimization thought: `abs(oh[0]-nh[0]) + abs(oh[1]-nh[1]) == 1` per candidate per opponent: fine.

Now let me reconsider `hpen` when can_coast and L < max_olen: fw=2.0, hpen=650 — I still eat at moderate risk to overtake the longer survivor. OK.

And when can_coast and L >= max_olen: fw=0.8, hpen=900 — pure survival. But what if the longer... I'm the longest → coasting to endgame with best length. But wait: what if a shorter snake keeps eating and overtakes me in the remaining turns? Remaining turns < my health - 5 ≤ 95. They could eat ~95/(dist between foods)... could grow +20 maybe. Hmm — should I keep eating to defend the lead? fw 0.8 still takes food when it's on the way/safe. The risk: dying needlessly. Keep 0.8. Fine.

Hmm, one more consideration — `can_coast` uses my_health but if I eat, health resets... coasting just requires survival; eating only helps. OK.

Now, let me reconsider the emergency threshold `my_health <= dmin + 6`: dmin = BFS distance to nearest food. Starvation occurs when health hits 0 after decrement. If health = d, I can take d-1 moves and eat on the d-th... eating on move d: health before eat = health - d... let me verify: at turn with health H, after moving health = H-1. Eat → 100. If H = d: after d moves, health = 0 → dead? "生命值降到 0：饿死" — during hunger step, health 1-1=0 → dead BEFORE eating? Order: move → hunger (subtract) → eat. If health becomes 0 at hunger step → dead even if on food?? Hmm! Order in rules: "2. 饥饿：每条蛇的生命值减 1" then "3. 吃食物". So if health drops to 0 in step 2, snake dies in step 4 (elimination judged after eating?). Elimination happens after eating — "降到 0：饿死" — the health reached 0 at step 2. Does eating in step 3 restore before the elimination check in step 4? Ambiguous! If a snake arrives on food with health 1: hunger → 0, eat → 100. Did it die? The elimination list: "生命值降到 0：饿死" — it DID reach 0. But then eat restored... 

Safest interpretation: reaching 0 at any point = dead. So I must eat while health ≥ 2 (arrive on food when health before the turn ≥ 2 → after decrement ≥ 1). So to be safe: must reach food within health - 1 moves. My emergency threshold `my_health <= dmin + 6` gives 6 turns of margin — good. Actually if the strict interpretation holds, arriving with health 1 → dies. My margin handles it (I'd arrive with health ~6).

Edge: health 1 right now → after this turn 0 → dead unless... eat this turn: hunger → 0 → die?? If interpretation is "0 = dead regardless", then at health 1 I'm doomed unless eating restores. Unknowable; my emergency mode tries to eat ASAP from health 12+ anyway.

Now, another important detail I should double check: **food respawn timing** — food eaten respawns immediately (step 5) at random empty cell. So dist_me to foods uses current foods ✓.

Next, `decide` must never return None. _decide always returns a name in all branches (cands nonempty → best_name set; cands empty → returns from names loop or random). ✓

Let me now double-check the `flood` function once more for an infinite loop — `seen` guards. ✓ deque pops. ✓

Performance micro-check: flood allocates tuples; fine.

One more consideration — maybe add a check: if a candidate nh is my OWN tail cell and I might eat... my tail retracts regardless (this turn) → safe ✓ (blocked handles dup case).

What about moving onto a cell where MY OWN body will... all handled by blocked (exact for self).

Hmm, wait — one more self-collision subtlety: my new head nh vs my body AFTER my move: my body = nh + b[0..L-2]. nh in b[0..L-2] → blocked ✓. nh == b[L-1] (tail, no dup) → free ✓. ✓

Also — the rules say hitting "any snake's body (excluding heads)". If nh == other snake's old head cell — as established, it's their neck after move → fatal. In blocked ✓. But WAIT — what if that other snake FAILS to move... all snakes always move (invalid dir → straight). What if their straight move is blocked/fatal for them — they still move there and die. Their old head cell still their neck. ✓

What if the other snake's body — hold on, what if other snake is length... their body [H, H, H] stacked: blocked = {H}. nh = H → fatal ✓.

OK now let me also think about whether I should model the case where an opponent moves into a cell I'm vacating — my old head cell — and I should NOT... no effect on me. ✓

Also — food under an opponent's head? Impossible (they'd have eaten it). ✓

Let me reconsider the -20 proximity penalty stacking with multiple bigger snakes in FFA — could be -100ish in a scrum → avoidance. OK.

Final check of weights sanity mid-game 1v1, health 60, fw=2.5, hpen=500: candidate A: food approach, fd=3, area 100 (capped 85 → 102), no risk: score ≈ 102 - 7.5 = 94.5. Candidate B: away from food, fd=5, area 120→102: 102-12.5=89.5. Picks A ✓. Candidate C: toward food but adjacent to longer opp head: 102 - 2.5 - 500-20 = -420 → avoided ✓.

Now — I realize the proximity penalty for md==1 & ol>=L applies even when nh is NOT enterable by them... it IS enterable (md==1, nh≠on). Same thing. Fine.

One more: should the md==2 & ol > L penalty exist? -4 mild. Keep.

Let me reconsider eq_pen in FFA = 500: both die = I die → same as hpen. Consistent.

Hmm, one thing about `min(eq_pen, hpen)` — in emergency hpen drops to 80-120; eq_pen FFA 500 → min → 120 → mutual-death gamble when starving. Both-die vs starve-later: tie vs lower rank... both dying same turn = tied with them, below everyone alive. Starving later = dying later = above them. Hmm! In FFA, if I starve in 8 turns, dying NOW in mutual head-on ranks me BELOW snakes that die in between... but above nobody extra... wait: mutual death now: I die at turn T. Starvation: I die at turn T+8. Rank: later death = better. So mutual death now is WORSE than starving later! So in FFA, when starving is inevitable anyway, dying later is still better. Unless I find food in those 8 turns (health drops → maybe I eat uncontested food). So eq_pen should stay HIGH (500) in FFA even when starving. Only pure-starvation-imminent (health ≤ 2, dmin > health) justifies gambling. Let me adjust: in FFA emergency, keep eq_pen 500, only lower if my_health <= 3 and dmin is not None and dmin >= my_health (certain death): then eq_pen=60. Hmm, also if dmin is None (no reachable food) and health < dmin... "certain death" when health <= (min manhattan food dist)+1? Ugh. Simplify FFA: eq_pen stays 500; when my_health <= 4: eq_pen = 60 (last resort gamble). In 1v1: mutual death = tie ≈ 0.5 vs starving = loss... wait 1v1: if I starve, I die, opponent survives → they win (rank 1). Mutual death now → tie. Tie > loss → gamble GOOD in 1v1 when starving is certain. So 1v1 emergency: eq_pen 100 already. Even more: certain-starve 1v1 → eq_pen 60.

Implement:

```python
    if dmin is not None and my_health <= dmin + 6:
        fw = max(fw, 8.0); hpen = min(hpen, 120)
        if n_opp == 1:
            eq_pen = min(eq_pen, 100)
    if my_health <= 12:
        fw = max(fw, 9.0); hpen = min(hpen, 80)
        if n_opp == 1:
            eq_pen = min(eq_pen, 60)
    if dmin is None and my_health < 25:
        fw = max(fw, 8.0); hpen = min(hpen, 100)
        if n_opp == 1:
            eq_pen = min(eq_pen, 80)
    if my_health <= 4:
        eq_pen = 60  # last resort
```

Hmm wait, hpen (longer snake kills me) in emergency: in FFA starving, dying now to a longer snake is worse than starving later → hpen should stay high in FFA too! Only gamble if certain death. Let me restrict: in FFA, emergency hpen reduction only when certain death: my_health <= 2 (about to starve, must eat NOW — dmin... if food reachable at dmin and health <= dmin+1 → can't survive → gamble now). Let me define certain_death = (dmin is not None and my_health <= dmin + 1) or my_health <= 3 or (dmin is None and ...). Then:

```python
    starving = (dmin is not None and my_health <= dmin + 6)
    certain = (dmin is not None and my_health <= dmin + 1) or my_health <= 3
    if starving:
        fw = max(fw, 8.0)
        if n_opp == 1:
            hpen = min(hpen, 150); eq_pen = min(eq_pen, 110)
    if certain:
        fw = max(fw, 9.0); hpen = min(hpen, 70); eq_pen = min(eq_pen, 60)
```

In FFA starving-but-not-certain: fw 8 (beeline) but hpen stays 500 — I won't gamble, I'll beeline and hope path clears / eat uncontested. Hmm — but if dmin is the nearest food and health <= dmin+6, beelining is right; risk penalties protect. OK.

In 1v1 starving: gamble more (tie beats loss). ✓

Also `dmin is None and my_health < 25` case: no reachable food — path might open up as bodies move. fw 8 toward nearest manhattan food; hpen unchanged (FFA) / reduced (1v1). Let me add:

```python
    if dmin is None and my_health < 30:
        fw = max(fw, 7.0)
        if n_opp == 1:
            hpen = min(hpen, 150); eq_pen = min(eq_pen, 100)
```

OK. Let me also double check `certain` when dmin None: my_health <= 3 → certain-ish. ✓ (covered by my_health <= 3).

Now, hpen=70 in "certain": gamble through longer snakes when otherwise dead. If they don't enter, I might reach food. OK.

Alright. Also one more thought: with fw=8-9 in emergencies, the food term (8 × fd) dominates everything except fatal/blocked — correct beeline.

Now let me also reconsider `hpen` values normal: 500 for longer. In 1v1 normal, being killed by longer opponent = loss (they survive). 500 vs area terms... fine.

Let me also double check that I never pick a candidate that's in `blocked` — filtered ✓. So no guaranteed-death moves except head-on gambles. 

Also — WAIT. One important miss: candidates filtered by `nh in blocked`, but what about nh occupied by a snake that will DIE this turn before... no — elimination judged simultaneously with my collision. Dead-this-turn snakes still count as bodies ("同时判定"). My blocked includes them ✓ conservative & correct per rules.

Hmm, actually let me reconsider: "死掉的蛇立刻从棋盘上消失" — step 4 elimination, then step 5 food. Within step 4, all conditions judged simultaneously — so a snake dying of wall-hit still has its body present for MY body-collision judgment. I believe blocked-includes-dying is correct. Edge case rarely matters.

Now — the free_time stall for dying snakes — irrelevant.

One more: snakes list order — fine.

Let me also reconsider: does the judge call decide for turn 1 with bodies stacked — my flood from nh: free_time of MY spawn cell = 1... nh adjacent; passing back through spawn cell at nd>=1 ✓.

Now — let me reexamine `cpen` (contention penalty) values: FFA 6. Foods contested when some opponent's manhattan < my BFS dist. In FFA crowded boards most foods contested → cost inflated uniformly; relative ranking still by dm mostly. OK.

I think code is complete. Let me also think about whether to add hysteresis for target only or also slight preference to keep... fine.

Let me write the final version, and double-check syntax carefully.

Also — I should double check `state["food"]` entries are lists [x, y] ✓ converted to tuples.

One more thing: `decide` catches exceptions from _decide, but if _decide returns an invalid move (bug), falls to _fallback ✓.

Let me also make sure no name collisions: inner functions bfs_dist, flood defined per call — slight overhead OK.

Potential subtle bug: in target selection loop I use variable name `f` and compare `f == _prev_target` — _prev_target is a tuple ✓.

Also `target` used in scoring: `fd = 60 + abs(nh[0]-target[0])...` — target not None there since field_t not None implies target not None ✓.

Final: consider `maxt` from state: e.g., 500. turn from 1. turns_left = maxt - turn + 1 ✓.

Let me also think — should safety_mode (can_coast) require being currently healthy... it IS my_health-based ✓.

Hmm, `can_coast = turns_left < my_health - 5`: at turn 490 of 500 (turns_left 11), health 40 → coast → fw 0.8, hpen 900 (if longest). Good: endgame safety.

Also if NOT longest and can_coast: fw 2.0 hpen 650 — still eats. OK.

Double-check: `if can_coast and L >= max_olen` — max_olen=0 if no opponents → coast mode when alone... game would be over. Fine.

Now — one more potential improvement I should consider: **avoiding the corner near bigger snakes** and **keeping an escape route**: flood area handles.

Also **don't chase food into a dead end where a bigger snake sits at the entrance** — area + risk handle.

OK, also let me reconsider the flood `extra_walls` for candidate: {nh} — should I also add other snakes' possible next-head cells? No.

Writing final code now. Let me also add small doc comments.

Also — re-examine the initial `for s in state["snakes"]` blocked-building: I iterate over ALL snakes incl. me. `others` list built earlier from same loop but with the `if not s.get("body"): continue` — note me might be skipped if empty body (weird) — then me is None → return random. OK. But blocked-building loop re-checks `if not b: continue` ✓.

Wait, there's an ordering issue: I build `others` in the first loop with the empty-body skip; but if MY body is empty, me=None → early return before using others. Fine.

Also `opp_info` uses `others` (already filtered for non-empty body) ✓. But `others` was appended in the loop `for s in state["snakes"]` — I appended even when body empty? Let me restructure cleanly:

```python
    snakes = [s for s in state["snakes"] if s.get("body")]
    me = None
    others = []
    for s in snakes:
        if s["id"] == me_id:
            me = s
        else:
            others.append(s)
```

Clean.

Now, one more think on flood area weighting `min(area, area_cap)*1.2` vs food weight fw up to 9 in emergency: emergency beeline: food term 9*fd diff ~ 9-45; area trap penalty up to (L+2)*40 ~ hundreds → still won't suicide into pockets when starving?? If starving, a pocket with food inside and area 5 (L=10): penalty (12-5)*40=280 + area 6 vs outside area 85: diff ~ -94+... 9*fd... if food in pocket at fd=2 vs outside fd=15: pocket: -280+6-18=-292; outside: -135+102... hmm outside = min(85,..)*1.2 - 15*9 = 102-135 = -33 → outside wins?? But food is IN the pocket — I need to enter to survive! Outside fd=15 means no path... if food unreachable from outside candidates, fd = 60+man → even worse for outside. So pocket (fd=2... wait candidates adjacent to pocket entrance...). This is getting complicated but roughly: pocket candidate score -292 vs outside -33+45(fd 20?)... The trap penalty kills me via starvation. Hmm! When starving (certain death otherwise), pocket entry is CORRECT even if trap-death follows (die later = better rank!). Trap death in 6 turns > starving in 4 turns. So trap penalty should ALSO shrink in emergency. Add: trap_pen_scale = 40 normally; if starving: 15; if certain: 5. Also area bonus weight maybe scale down in emergency. Let me add trap_pen variable:

```python
    trap_pen = 40.0
    if starving: trap_pen = 18.0
    if certain: trap_pen = 6.0
    ...
    if area <= L + 1:
        score -= (L + 2 - area) * trap_pen
```

Also, area bonus 1.2 per cell vs food 9/cell: fd diffs ~10 → 90 points vs area diffs up to ~100 — comparable; fine.

Define `starving` and `certain` before weights:

```python
    starving = (dmin is not None and my_health <= dmin + 6) or (dmin is None and my_health < 30)
    certain = (dmin is not None and my_health <= dmin + 1) or my_health <= 3
```

Then weights:

```python
    if can_coast and L >= max_olen:
        fw, hpen = 0.8, 900
    elif can_coast:
        fw, hpen = 2.0, 650
    elif my_health > 85: fw, hpen = 1.8, 500
    elif my_health > 50: fw, hpen = 2.5, 500
    elif my_health > 30: fw, hpen = 4.0, 420
    else: fw, hpen = 6.5, 320
    eq_pen = 140 if n_opp == 1 else 500
    if starving:
        fw = max(fw, 8.0)
        if n_opp == 1:
            hpen = min(hpen, 150); eq_pen = min(eq_pen, 110)
    if certain:
        fw = max(fw, 9.0); hpen = min(hpen, 70); eq_pen = min(eq_pen, 60)
    trap_pen = 40.0
    if starving: trap_pen = 16.0
    if certain: trap_pen = 6.0
```

Note in FFA starving: hpen stays (500) — correct per rank logic (die later). In FFA certain: hpen 70 — gamble since dead anyway. Hmm wait — in FFA "certain" death: gambling through a LONGER snake: if I enter and they enter, I die NOW (worse than starving in 2 turns). If they don't enter, I might survive. Probability they enter < 0.5 typically. Expected death turn: p*now + (1-p)*(survive or starve). If certain death = starve at T+2: p*(T) + (1-p)*(T+2) < T+2 always → gamble is weakly better in expectation of surviving later... if gamble succeeds I might eat and live long. Yes gamble. ✓ eq_pen 60 in certain: mutual death now vs starve in 2: now is WORSE (rank). Hmm! In FFA certain: mutual-death-now ranks below starve-later. So eq_pen should stay 500 in FFA even when certain?? If I starve at T+2, I rank above anyone dying at T. Mutual death at T ties with them, below later-diers. So never take mutual-death gamble in FFA when any survival chance remains. Only gamble vs LONGER snakes (they might not come). So: certain → hpen 70, but eq_pen: FFA keep 500... but wait, if death is certain in 2 turns, and the food cell is contested by an EQUAL snake who also must eat — they also gamble?... If they enter and I enter, both die at T; if I avoid, I starve at T+2, they eat and live. eq_pen 500 → I avoid → starve → rank above them. That's actually BETTER for ranking than mutual death! Yes: eq_pen stays 500 in FFA always. And 1v1: mutual death = tie beats loss → gamble (60). ✓ So:

```python
    if certain:
        fw = max(fw, 9.0); hpen = min(hpen, 70)
        if n_opp == 1:
            eq_pen = min(eq_pen, 60)
```

And starving 1v1: hpen 150, eq_pen 110. FFA starving: hpen 500 (unchanged), eq_pen 500 (unchanged). Wait but FFA starving with hpen 500: I beeline food but won't pass adjacent-to-longer-head cells... if food adjacent to longer head, I orbit until they take it or my health drops to certain → then gamble. Since certain-death gambling triggers only at health <= dmin+1... hmm, at that point I'm 1 turn from starving; the food may be gone. Ehh. Let me soften FFA starving hpen a bit: 300? Rank logic says avoid death-now vs starve-later... The expected-value calc: gamble now with prob p of dying now, (1-p) of maybe surviving. If I starve at T+k for sure, gambling: p·T + (1-p)·(survival). If (1-p) survival chance is decent and p < 0.5, worth it. Food cell adjacent to longer head: p maybe 0.3 → EV better. Set FFA starving hpen = 250. Compromise. OK:

```python
    if starving:
        fw = max(fw, 8.0)
        if n_opp == 1:
            hpen = min(hpen, 150); eq_pen = min(eq_pen, 110)
        else:
            hpen = min(hpen, 250)
```

Fine. These are heuristics anyway.

Also — `starving` includes dmin None & health<30: fw 8 toward manhattan-nearest food. OK.

Now — final structure done. Let me also double check `certain` when dmin is None and health <= 3 → certain ✓ via my_health<=3.

One more review of flood usage in squeeze: `opp_base = flood(opp_head, {opp_head})` — but opp_head is in blocked; flood doesn't care ✓. extra_walls {opp_head} prevents... start seen anyway. Actually extra_walls={opp_head} matters for NEIGHBOR expansion: neighbors c != opp_head... c == opp_head is `c in seen` already. So extra_walls redundant but harmless.

Wait, actually there's a subtlety in squeeze flood: I want opponent's space AFTER this turn (their head moved). Flooding from their CURRENT head with current blocked approximates region around them. Fine.

Also `a2 = flood(opp_head, {opp_head, nh})` — nh as extra wall ✓.

But squeeze flood from opp_head — their own body cells around them are in free_time with stall 2 → their own body counted as eventually-free → their "space" includes their own body cells?? The flood from their head passes through their own body cells after stall time → overestimates their area hugely (their body always trails them). Hmm — their body cells free as THEY move (they're moving too), so it's roughly OK — their body vacates cells as they advance. It's the same optimism I apply to my own flood. Consistent. Fine.

Also for MY flood: my body cells free per free_time (stall 1) — my body vacates as I move — but the flood path IS my hypothetical movement; cells my flood-path "occupies" aren't accounted (flood doesn't persist my future head cells as walls). Optimistic (classic flood-fill limitation). Accept.

OK also one more consideration — `area` might be inflated by cells behind opponents' heads that they'll claim. Known limitation. The trap penalty and risk penalties mitigate.

Now, let me finalize and also double check Python syntax by writing the whole file mentally:

```python
import random
from collections import deque

DIRS = (("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0))
VALID = ("up", "down", "left", "right")

_prev_target = None


def decide(state):
    try:
        mv = _decide(state)
        if mv in VALID:
            return mv
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        pass
    return random.choice(VALID)


def _fallback(state):
    try:
        w = state["width"]
        h = state["height"]
        me = None
        for s in state["snakes"]:
            if s["id"] == state["you"]:
                me = s
                break
        if me is None or not me["body"]:
            return random.choice(VALID)
        body = [(p[0], p[1]) for p in me["body"]]
        head = body[0]
        neck = body[1] if len(body) > 1 else (-99, -99)
        blocked = set(body[:-1])
        if len(body) >= 2 and body[-1] == body[-2]:
            blocked.add(body[-1])
        straight = None
        if head != neck:
            v = (head[0] - neck[0], head[1] - neck[1])
            for name, dx, dy in DIRS:
                if (dx, dy) == v:
                    straight = name
                    break
        order = list(DIRS)
        if straight is not None:
            order.sort(key=lambda d: d[0] != straight)
        for name, dx, dy in order:
            nh = (head[0] + dx, head[1] + dy)
            if nh == neck:
                continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h and nh not in blocked:
                return name
        for name, dx, dy in order:
            nh = (head[0] + dx, head[1] + dy)
            if nh == neck:
                continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h:
                return name
    except Exception:
        pass
    return random.choice(VALID)
```

Note: in _fallback, `blocked = set(body[:-1])` — includes my head & neck. For len-1 body: body[:-1] empty; add head: `if len(body)==1: blocked.add(head)`. Add.

Now _decide full:

I'll write it out completely now (final):

```python
def _decide(state):
    global _prev_target
    w = state["width"]
    h = state["height"]
    turn = state.get("turn", 1)
    maxt = state.get("max_turns", 500)
    me_id = state["you"]

    snakes = [s for s in state["snakes"] if s.get("body")]
    me = None
    others = []
    for s in snakes:
        if s["id"] == me_id:
            me = s
        else:
            others.append(s)
    if me is None:
        return random.choice(VALID)

    my_body = [(p[0], p[1]) for p in me["body"]]
    L = len(my_body)
    head = my_body[0]
    neck = my_body[1] if L > 1 else (-99, -99)
    my_health = me["health"]
    foods = [(f[0], f[1]) for f in state["food"]]
    foodset = set(foods)

    blocked = set()
    free_time = {}
    for s in snakes:
        b = [(p[0], p[1]) for p in s["body"]]
        sl = len(b)
        if sl == 0:
            continue
        stall = 1 if s["id"] == me_id else 2
        dup = sl >= 2 and b[-1] == b[-2]
        for i in range(sl):
            c = b[i]
            if i < sl - 1 or dup or sl == 1:
                blocked.add(c)
            if sl == 1:
                t = 3
            elif i == sl - 1 and not dup:
                t = 0
            else:
                t = sl - 1 - i + stall
            if c not in free_time or t < free_time[c]:
                free_time[c] = t

    opp_info = []
    for s in others:
        b = [(p[0], p[1]) for p in s["body"]]
        oh = b[0]
        on = b[1] if len(b) > 1 else (-99, -99)
        opp_info.append((oh, on, len(b)))
    n_opp = len(opp_info)

    def bfs_dist(start):
        dist = {start: 0}
        dq = deque([start])
        while dq:
            cur = dq.popleft()
            x, y = cur
            d = dist[cur] + 1
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    n = (nx, ny)
                    if n not in dist and n not in blocked:
                        dist[n] = d
                        dq.append(n)
        return dist

    def flood(start, extra_walls):
        seen = {start}
        cnt = 1
        dq = deque([(start[0], start[1], 0)])
        while dq:
            x, y, d = dq.popleft()
            nd = d + 1
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    c = (nx, ny)
                    if c in seen or c in extra_walls:
                        continue
                    ft = free_time.get(c)
                    if ft is not None and nd < ft:
                        continue
                    seen.add(c)
                    cnt += 1
                    dq.append((nx, ny, nd))
        return cnt

    dist_me = bfs_dist(head)
    dmin = None
    for f in foods:
        if f in dist_me:
            dd = dist_me[f]
            if dmin is None or dd < dmin:
                dmin = dd

    cpen = 2 if n_opp == 1 else 6
    if my_health < 30:
        cpen = 0
    target = None
    best_cost = None
    for f in foods:
        if f in dist_me:
            dm = dist_me[f]
            contested = 0
            for oh, _on, _ol in opp_info:
                if abs(oh[0] - f[0]) + abs(oh[1] - f[1]) < dm:
                    contested = 1
                    break
            cost = dm + contested * cpen
        else:
            cost = 150 + abs(head[0] - f[0]) + abs(head[1] - f[1])
        if f == _prev_target:
            cost -= 1.5
        if best_cost is None or cost < best_cost:
            best_cost = cost
            target = f
    _prev_target = target
    field_t = bfs_dist(target) if target is not None else None

    turns_left = maxt - turn + 1
    max_olen = 0
    for _oh, _on, ol in opp_info:
        if ol > max_olen:
            max_olen = ol
    can_coast = turns_left < my_health - 5

    starving = ((dmin is not None and my_health <= dmin + 6)
                or (dmin is None and my_health < 30))
    certain = ((dmin is not None and my_health <= dmin + 1) or my_health <= 3)

    if can_coast and L >= max_olen:
        fw, hpen = 0.8, 900.0
    elif can_coast:
        fw, hpen = 2.0, 650.0
    elif my_health > 85:
        fw, hpen = 1.8, 500.0
    elif my_health > 50:
        fw, hpen = 2.5, 500.0
    elif my_health > 30:
        fw, hpen = 4.0, 420.0
    else:
        fw, hpen = 6.5, 320.0
    eq_pen = 140.0 if n_opp == 1 else 500.0
    if starving:
        fw = max(fw, 8.0)
        if n_opp == 1:
            hpen = min(hpen, 150.0)
            eq_pen = min(eq_pen, 110.0)
        else:
            hpen = min(hpen, 250.0)
    if certain:
        fw = max(fw, 9.0)
        hpen = min(hpen, 70.0)
        if n_opp == 1:
            eq_pen = min(eq_pen, 60.0)
    trap_pen = 40.0
    if starving:
        trap_pen = 16.0
    if certain:
        trap_pen = 6.0

    area_cap = (w * h) // 3 + 10

    squeeze_k = 0.0
    opp_head = None
    opp_base = 0
    if n_opp == 1:
        oh, _on, ol = opp_info[0]
        opp_head = oh
        opp_base = flood(oh, {oh})
        if not can_coast and my_health > 35:
            squeeze_k = 2.0 if L > ol + 1 else 0.4

    straight = None
    if L > 1 and head != neck:
        v = (head[0] - neck[0], head[1] - neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == v:
                straight = name
                break

    cands = []
    for name, dx, dy in DIRS:
        nh = (head[0] + dx, head[1] + dy)
        if nh == neck:
            continue
        if not (0 <= nh[0] < w and 0 <= nh[1] < h):
            continue
        if nh in blocked:
            continue
        cands.append((name, nh))

    if not cands:
        names = []
        if straight is not None:
            names.append(straight)
        for n, _dx, _dy in DIRS:
            if n != straight:
                names.append(n)
        for n in names:
            for dn, dx, dy in DIRS:
                if dn == n:
                    nh = (head[0] + dx, head[1] + dy)
                    if nh != neck and 0 <= nh[0] < w and 0 <= nh[1] < h:
                        return n
        return random.choice(VALID)

    best_score = None
    best_name = None
    for name, nh in cands:
        score = 0.0
        for oh, on, ol in opp_info:
            if abs(oh[0] - nh[0]) + abs(oh[1] - nh[1]) == 1 and nh != on:
                if ol > L:
                    score -= hpen
                elif ol == L:
                    score -= min(eq_pen, hpen)
        area = flood(nh, {nh})
        if area <= L + 1:
            score -= (L + 2 - area) * trap_pen
        score += min(area, area_cap) * 1.2
        if field_t is not None:
            fd = field_t.get(nh)
            if fd is None:
                fd = 60 + abs(nh[0] - target[0]) + abs(nh[1] - target[1])
            score -= fd * fw
        for oh, on, ol in opp_info:
            md = abs(oh[0] - nh[0]) + abs(oh[1] - nh[1])
            if md == 1:
                if ol >= L:
                    score -= 20.0
                else:
                    score += 2.0
            elif md == 2 and ol > L:
                score -= 4.0
        if squeeze_k > 0:
            a2 = flood(opp_head, {opp_head, nh})
            gain = opp_base - a2
            if gain > 0:
                score += min(gain, 60) * squeeze_k
        if name == straight:
            score += 0.15
        score += random.random() * 0.3
        if best_score is None or score > best_score:
            best_score = score
            best_name = name
    return best_name
```

Wait — bug: in the head-on risk loop, the `nh != on` check: on could be (-99,-99); fine. But also — if ol < L (shorter), no penalty (they die). ✓ 

Check: `field_t.get(nh)` — fd could be 0 when nh == target ✓.

One more: `_prev_target` when foods empty: target None; `_prev_target = None` ✓.

Check `starving` when dmin is None and my_health < 30 — includes health 29 with unreachable food: fw 8 beeline toward manhattan target (fd=60+man) — hmm, fd 60+man × 8 = ~500+ dominates all — beelines toward possibly-unreachable food. If food truly unreachable (walled off), I crash into walls of bodies... blocked cells are never candidates; I'd push against the wall area — acceptable (maybe it opens). OK.

Another check: `certain` when dmin None: health <= 3. ✓

Now — subtle: `starving` uses dmin from BFS through static walls; if food is behind my own body (reachable after tail moves), dmin None → starving triggers early (health<30) → fw 8. OK fine.

Double-check hpen never exceeds... fine.

Potential runtime: worst case per turn: bfs_dist ×2 (~2×961 expansions), flood ×(3 + 4) ≈ 7×961 ≈ 7k expansions; each expansion ~ 4 neighbor ops with tuple creation and dict/set lookups → ~30 dict ops → ~200k dict ops ≈ 20-40ms in CPython? Hmm, that might be tight-ish but OK. Actually 961 cells × 4 neighbors = ~4k lookups per flood; 7 floods = 28k; plus 2 BFS = 8k → ~36k lookups, each ~0.1-0.3µs → ~10ms. Fine. Tuple hashing of ints is fast. OK.

But wait — squeeze floods only when n_opp==1 (15x15 board): flood = 225 cells — trivial. FFA: no squeeze. So per turn: 2 BFS + 3 floods on 31x31 → ~14k lookups → ~5ms. 

One more possible improvement: flood area for FFA with 10 opponents — maybe also cap iteration... it's fine.

Now, let me reconsider once more the decision NOT to model other snakes' next heads in flood. Consider FFA scrum: my area computed includes cells opponents will occupy → overestimate → I might enter a shrinking region and die via body collision next turn... but each turn I re-eval; body collisions arise when I have no safe move — the trap penalty at that point... Eh. Standard risk. Could add: in flood, treat cells adjacent to other snakes' heads as... let me add a small penalty instead: estimate "crowding": count opponents within manhattan 3 of nh; score -= crowd * 8? In FFA that discourages scrums further. Hmm — I already have md==1/2 penalties. Add md<=3 → -2 per bigger... Keep as is. Enough.

One more critical review of the dup/blocked logic for OTHER snakes whose body length ≥2: `i < sl-1 or dup` → blocked. For i = sl-1 (tail) with dup → blocked ✓; without dup → not blocked ✓.

Edge: what about a snake whose body is exactly 2 cells [c, c]? Can't happen (min 3), but handled: dup → blocked {c} ✓.

Now — think about whether `bfs_dist(target)` includes `target` as start even though... target not blocked ✓.

What if two foods and target == prev: cost -1.5 ✓.

What about the extremely important detail: does eating this turn cause me to be LONGER for THIS turn's head-on comparisons? Earlier I showed comparison reduces to ol vs L (same food flag). But wait — one more case: nh has food; my L vs ol comparison — but what if THE OTHER snake enters nh... both eat. ol vs L ✓. What if other snake enters a DIFFERENT food cell and I enter nh (no food)? Different cells — head-on doesn't apply unless same cell. ✓ Fine.

But hmm, there's ANOTHER growth nuance: my "length" for head-on at future turns uses grown lengths — handled naturally as turns pass.

Now — the last significant thing to double check: **the U-turn rule direction inference**. The engine: "掉头（走回自己脖子那一格）无效，按原方向继续走". My neck = body[1] (after last move, body[0] is current head, body[1] is where head was = previous head position). "原方向" = direction from body[1] to body[0]... i.e., the direction I moved last turn. Moving "back to neck" = direction head→neck = reverse. My filter: nh == neck excluded ✓. My `straight` = head - neck = last move direction ✓.

Edge: stacked start: neck == head → "原方向" undefined; engine presumably accepts any move (or maybe picks something). All 4 moves go to cells ≠ neck(==head). But wait — could the engine consider a move to ANY adjacent cell as "走回脖子" when neck==head? The neck cell IS the head cell; moving to any adjacent cell ≠ neck cell. So no U-turn possible. But what does engine do if... fine.

Hmm, one more potential edge: what if the engine treats "原方向" for the very first move as something specific and my move is fine. Not an issue since I never emit neck-reversal.

Now let me also think about the module-level `random` usage: judge pre-imports and seeds `random` — "random 模块已经由裁判按每局的种子初始化，可以直接 import random 使用". I import random and use random.random() and random.choice — ✓ deterministic per game.

Potential issue: my jitter makes behavior deterministic given seed — same inputs → same outputs; fine.

Final syntax check on tricky lines:

- `order.sort(key=lambda d: d[0] != straight)` in _fallback — d is a tuple ("up",0,-1); d[0] != straight → False(0) for straight → sorted first ✓.

- `if mv in VALID` — tuple membership ✓.

Let me reconsider `can_coast` boundary: `turns_left < my_health - 5`. my_health after this turn decreases by 1 each turn; at the last turn (turns_left=1): health after = my_health-1 ≥ 1 required → my_health ≥ 2... coast condition needs my_health > turns_left + 5. Fine.

Also one more consideration: **hpen=900 in coast mode** — even eq_pen min(140, 900)... eq_pen stays 140 in 1v1 coast — mutual death in coast mode (when I'm longest) = tie instead of win — bad! In coast mode, I should also avoid equal-length gambles. eq_pen = min(eq_pen, hpen)? In coast mode with L >= max_olen and n_opp==1, equal length impossible (L >= max_olen means no equal... equal possible if L == max_olen? L >= max_olen includes equality — an equal-length opponent exists → mutual death ties. Let me change coast condition to L >= max_olen and eq_pen → set eq_pen = min(eq_pen, hpen) in coast... Actually simpler: eq_pen = min(eq_pen, hpen) globally at the end! In normal play hpen=500 ≥ eq_pen(140/500) → no change. In emergencies hpen < eq_pen → eq_pen shrinks — wait I specifically wanted eq_pen HIGH in FFA emergency (mutual death worse than starving later) while hpen low (gamble vs longer). Hmm — conflict: min(eq_pen, hpen) would lower FFA eq_pen in emergencies — NOT wanted. Keep them separate, but in coast mode explicitly raise eq_pen: if can_coast and L >= max_olen: eq_pen = 800 (unless certain-death). Let me add that.

Also in coast mode but NOT longest (fw 2.0, hpen 650): eq_pen — need to outgrow the longer one... mutual death = tie ≈ current-loss... keep 140 in 1v1. OK.

So after computing eq_pen etc., add:

```python
    if can_coast and L >= max_olen:
        eq_pen = max(eq_pen, 800.0)
```

(but `certain` already lowered... order: compute base weights, then starving/certain adjustments, then coast override? Coast and starving can't co-occur meaningfully (coast = healthy). If both... coast health > turns_left+5; starving = health ≤ dmin+6; possible dmin large... then fw max'd. Edge case, fine. Let me place coast eq_pen override after starving/certain blocks but skip if certain:

Actually simplest: at the very end:

```python
    if can_coast and L >= max_olen and not certain:
        eq_pen = 800.0
        hpen = 900.0
        fw = 0.8
```

Let me restructure the weight block cleanly:

```python
    # base
    if my_health > 85: fw, hpen = 1.8, 500.0
    elif my_health > 50: fw, hpen = 2.5, 500.0
    elif my_health > 30: fw, hpen = 4.0, 420.0
    else: fw, hpen = 6.5, 320.0
    eq_pen = 140.0 if n_opp == 1 else 500.0
    # coasting (can survive to turn limit without food)
    if can_coast:
        if L >= max_olen:
            fw, hpen, eq_pen = 0.8, 900.0, 800.0
        else:
            fw, hpen = 2.0, 650.0
    # starvation
    if starving: ...
    if certain: ...
    trap_pen = ...
```

Coast before starving adjustments — starving overrides (can't coast if starving... both can't be true: coast needs health > turns_left+5; starving needs health ≤ dmin+6; if dmin > turns_left, both true?? e.g., turns_left=10, health 60 (coast: 10 < 55 ✓), dmin=80?? dmin ≤ board diameter+ ~ 60 on 31x31... dmin 55, health 60 ≤ 61 → starving → fw 8 beeline food... but I don't need food to survive to limit (coast)! Starving flag wrong here: food unreachable within health — but game ends first. Fix: starving only matters if starvation before turn limit: starving = dmin is not None and my_health <= dmin + 6 and (dmin < turns_left)... eh: if turns_left < my_health, I survive to end regardless → not starving. Add: `if turns_left < my_health - 5: starving = False` (coast implies not starving). Actually: starving condition should be: I will hit 0 health before the turn limit without food: my_health - 1*turns... if my_health > turns_left + 1, health never reaches 0 within game → not starving. So:

```python
    safe_to_end = my_health > turns_left + 1
    starving = (not safe_to_end) and ((dmin is not None and my_health <= dmin + 6) or (dmin is None and my_health < 30))
    certain = (not safe_to_end) and ((dmin is not None and my_health <= dmin + 1) or my_health <= 3)
```

Hmm, `my_health <= 3` with safe_to_end... health 3, turns_left 1 → next turn health 2, game over — fine not certain. But `my_health <= 3` regardless... if safe_to_end and health ≤ 3 — impossible (turns_left ≥ ... health 3 > turns_left+1 → turns_left < 2 → last turn). OK whatever, edge.

And coast condition = safe_to_end basically. can_coast = my_health > turns_left + 5 (margin). Use safe_to_end for starving/certain suppression and can_coast for weight change. Good.

Also `certain` with safe_to_end → False. ✓

Now the FFA-vs-1v1 starving distinction stays.

I think we're good. One more consideration — trap check `area <= L + 1`: with time-aware flood, following my own tail in a corridor: area counts the loop; if loop ≥ L, survivable. Threshold L+1 reasonable.

Let me also think about a potential pathology: food spawns in a 1-cell pocket; I go in (fd small), area ~1 → trap penalty (L+1)*40 huge → I won't enter unless starving with food... even then trap_pen 6-16: (L+2-1)*16 ~ 150ish vs fd*8... if food IS in the pocket, fd to pocket = small... entering: score = -(L+1)*16 + 1.2 + 0; alternative: fd larger... e.g., L=5: entering pocket: -96+1.2 = -95; staying out: fd maybe 5 → -40 + area 100: -40+102=62 → stays out. Starves later rather than trap-dies now. If starving (dmin = 1, health 7): trap_pen 16: enter: -96+1.2-8=-103; out: fd... out candidates fd = 60+man? If pocket food is target and unreachable from out-candidates: fd ~ 62 → -496+102 → enter! OK enters when starving. Decent.

Hmm wait, but there's an inconsistency: when starving and food in pocket, target = that food (dmin=1). Out candidates: field_t.get(nh) → pocket entrance... the entrance cell IS reachable (fd=1?) — entrance cell adjacent to food... The candidate that enters the pocket mouth has fd=1; only going INSIDE (to the food cell itself) has fd=0. The trap penalty applies at the mouth entry. Fine — the bot evaluates mouth: area (time-aware) counts pocket cells: 2 cells (mouth + food cell)... area=2 ≤ L+1 → penalty → avoids → orbits. As health drops to certain → trap_pen 6 → enters. Dies after eating (trapped) — but ate → survived a bit longer. Rank-wise OK.

Actually hmm — one-cell pocket + food: enter, eat (length+1, tail dup), next turn: mouth exit... mouth cell is free (nothing there). Not trapped at all! area from food cell = 2 (food cell + mouth). Trap penalty applied but actually fine. Whatever — time-aware flood correctly counts 2 cells; penalty (L+2-2)*40 — overcautious for pockets that OPEN. Fine, safe bias.

OK — I also want to reconsider trap threshold with time-aware flood: in open space area huge → no penalty. Good.

Now let me finalize. Also double-check: `for oh, _on, _ol in opp_info` variable naming — fine.

One last thing: the judge says timeouts etc. handled; my code is fast. Exceptions caught. Return values valid strings. 

Also: "连续 3 次" misbehavior → straight forever. My try/except prevents.

Let me also quickly re-examine: in `decide`, if `_decide` returns something not in VALID (impossible), fallback. ✓

One more scan for NameError risks: `target` used in scoring when `field_t is not None` → implies target not None ✓. `opp_head` used when squeeze_k>0 → set ✓. `straight` initialized None ✓. `best_name` returned — set since cands nonempty ✓.

In no-cands branch: `names` loop — returns first in-bounds non-neck direction (straight preferred). Note: this may be a blocked cell (fatal) but all options fatal anyway. ✓

Also — hmm, one more thought: the no-cands case could arise when I'm boxed in by bodies but a head-on cell exists... no wait: head-on cells are free cells (not blocked) → they'd be in cands. no-cands = every non-neck in-bounds neighbor is blocked/out → truly dead this turn (or... one exotic escape: a neighbor blocked only by a snake that will DIE this turn (wall-hit) — "同时判定" says still fatal. OK.)

Hmm — actually wait, one more: is a neighbor blocked by a DYING snake really fatal? Let me re-read: "淘汰（同时判定）：头走出棋盘：死..." — all four conditions listed then judged simultaneously. So if opponent walks out of board, my head hitting their body — is their body "any snake body" at judgment time? The judgment is simultaneous; their body existed during the move step. I'll trust fatal (conservative). Also rule 5: dead snakes disappear AFTER elimination. So during elimination, the body... "死掉的蛇立刻从棋盘上消失" — ambiguous ordering within step 4. Conservative = treat as fatal. My code does. ✓ (If actually safe, I miss rare escape chances — acceptable.)

Now — FINAL concern: performance of `flood` when called with squeeze per candidate in 1v1: fine.

Also — realize I should double-check `blocked` includes OTHER snakes' tails correctly when dup: dup means THEY just ate; their tail cell stays. My candidate entering their tail cell → fatal ✓ blocked includes it.

And when NOT dup: their tail free ✓ not blocked.

Great. One more small thing: `free_time` for their non-dup tail = 0 — passable immediately in flood — but it's also potentially where THEIR head... no, their head is elsewhere. ✓

Also in flood: cells never in free_time (never body) → passable always ✓.

Alright — also add small feature: prefer moves that keep me adjacent to my own tail when nothing else matters? The area term covers.

Let me also reconsider whether to include "head-cell-adjacent cells of LONGER snakes as flood-blocked" — i.e., pessimistic area. Skip.

DONE. Write final answer. Also need the ≤300 char strategy summary after the code block.

Actually — hold on, let me reconsider one more time the flood `extra_walls` for candidates: {nh}. Should extra_walls also include... the cells that will be occupied by my new body are nh + b[0..L-2] — b cells are in free_time with my stall — flood passes through my old body cells after they free — correct time-aware semantics ✓ (my body cells DO free as I move along the flood path — approximately).

One more idea — should I make the flood stop early for perf? Not needed.

Also — one more important detail about time-aware flood and the trap check: `area <= L+1` uses count of eventually-reachable cells; in a corridor behind a longer snake, area counts cells that open as THEIR body moves — could overestimate (their body advances and fills new cells of that corridor). Known optimism. Accept.

Also consider making trap check `area <= L` instead of L+1 — marginal. Keep L+1.

Final code assembly. Let me count roughly the ~180 lines. Fine.

Wait, one more potential bug: in `_decide`, `neck = my_body[1] if L > 1 else (-99, -99)` — then `if L > 1 and head != neck` for straight. But in candidate filter: `if nh == neck: continue` — neck (-99,-99) never matches ✓.

And the head==neck stacked case: L=3, all same → neck == head; `nh == neck` never true (nh is neighbor) ✓ all 4 candidates.

Also for stacked: straight=None ✓ (head==neck).

Also — hmm, if head == neck (stacked), can I move to any of the 4? Yes (none is the neck cell since neck==head and nh≠head). ✓

Edge: what if L==2 somehow with body [a,b] distinct: neck=b ✓ works.

OK also one FINAL strategic review for the FFA: 11 snakes, my survival-first bot with food-chasing when uncontested. Expected outcome: mid-high survival, medium length → likely ranks well since many aggressive bots die. In 1v1: solid food efficiency + safety. Good enough.

One more micro-thing: `cpen` FFA=6 vs contested if ANY opponent manhattan < my BFS dist. In 11-snake FFA, nearly all foods contested → cost = dm + 6 uniformly → effectively nearest-food chasing. Maybe use count-scaled: contested_count? cost = dm + min(#contesters,3)*2? Let me do: cost = dm + 2*min(contesters, 3) in FFA (so heavily contested food avoided more), and 1v1: dm + (2 if contested else 0). Let me implement contesters count:

```python
    for f in foods:
        if f in dist_me:
            dm = dist_me[f]
            contesters = 0
            for oh, _on, _ol in opp_info:
                if abs(oh[0]-f[0]) + abs(oh[1]-f[1]) < dm:
                    contesters += 1
            if n_opp == 1:
                cost = dm + (2 if contesters else 0)
            else:
                cost = dm + 2 * min(contesters, 3)
```

OK.

Also health<30 → cpen=0: keep as `if my_health < 30: contesters = 0`... incorporate: skip contest penalty when health < 30. Fine — compute flag first.

Write it final now.

Also the summary ≤300 chars (Chinese). Something like:

"策略：生存优先的单步评估。每回合对每个可行方向打分：精确判定本回合致命格（含尾巴缩回、刚进食尾巴不动），对可能被更长/等长蛇头抢入的格子重罚；用时间感知洪泛（蛇身随回合释放）估算活动空间防死胡同；BFS选食物目标（考虑争抢程度），按血量调整觅食权重，低血/断粮时提升觅食权重并允许冒险；仅剩一条对手且我更长时挤压其空间；回合将尽且血量够撑到终局时转纯保命。"

That's ~200 chars. Good.

Let me write out the complete final file, carefully.

```python
# bot.py
import random
from collections import deque

DIRS = (("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0))
VALID = ("up", "down", "left", "right")

_prev_target = None


def decide(state):
    try:
        mv = _decide(state)
        if mv in VALID:
            return mv
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        pass
    return random.choice(VALID)


def _fallback(state):
    try:
        w = state["width"]
        h = state["height"]
        me = None
        for s in state["snakes"]:
            if s["id"] == state["you"]:
                me = s
                break
        if me is None or not me["body"]:
            return random.choice(VALID)
        body = [(p[0], p[1]) for p in me["body"]]
        head = body[0]
        neck = body[1] if len(body) > 1 else (-99, -99)
        blocked = set(body[:-1])
        if len(body) == 1:
            blocked.add(head)
        if len(body) >= 2 and body[-1] == body[-2]:
            blocked.add(body[-1])
        straight = None
        if head != neck:
            v = (head[0] - neck[0], head[1] - neck[1])
            for name, dx, dy in DIRS:
                if (dx, dy) == v:
                    straight = name
                    break
        order = list(DIRS)
        if straight is not None:
            order.sort(key=lambda d: d[0] != straight)
        for name, dx, dy in order:
            nh = (head[0] + dx, head[1] + dy)
            if nh == neck:
                continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h and nh not in blocked:
                return name
        for name, dx, dy in order:
            nh = (head[0] + dx, head[1] + dy)
            if nh == neck:
                continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h:
                return name
    except Exception:
        pass
    return random.choice(VALID)


def _decide(state):
    global _prev_target

    w = state["width"]
    h = state["height"]
    turn = state.get("turn", 1)
    maxt = state.get("max_turns", 500)
    me_id = state["you"]

    snakes = [s for s in state["snakes"] if s.get("body")]
    me = None
    others = []
    for s in snakes:
        if s["id"] == me_id:
            me = s
        else:
            others.append(s)
    if me is None:
        return random.choice(VALID)

    my_body = [(p[0], p[1]) for p in me["body"]]
    L = len(my_body)
    head = my_body[0]
    neck = my_body[1] if L > 1 else (-99, -99)
    my_health = me["health"]
    foods = [(f[0], f[1]) for f in state["food"]]

    # ---- occupancy model for this turn ----
    blocked = set()    # cells that are fatal to enter this turn
    free_time = {}    # cell -> earliest flood step at which it becomes passable
    for s in snakes:
        b = [(p[0], p[1]) for p in s["body"]]
        sl = len(b)
        if sl == 0:
            continue
        stall = 1 if s["id"] == me_id else 2
        dup = sl >= 2 and b[-1] == b[-2]
        for i in range(sl):
            c = b[i]
            if i < sl - 1 or dup or sl == 1:
                blocked.add(c)
            if sl == 1:
                t = 3
            elif i == sl - 1 and not dup:
                t = 0
            else:
                t = sl - 1 - i + stall
            if c not in free_time or t < free_time[c]:
                free_time[c] = t

    opp_info = []
    for s in others:
        b = [(p[0], p[1]) for p in s["body"]]
        oh = b[0]
        on = b[1] if len(b) > 1 else (-99, -99)
        opp_info.append((oh, on, len(b)))
    n_opp = len(opp_info)

    # ---- helpers ----
    def bfs_dist(start):
        dist = {start: 0}
        dq = deque([start])
        while dq:
            cur = dq.popleft()
            x, y = cur
            d = dist[cur] + 1
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    n = (nx, ny)
                    if n not in dist and n not in blocked:
                        dist[n] = d
                        dq.append(n)
        return dist

    def flood(start, extra_walls):
        seen = {start}
        cnt = 1
        dq = deque([(start[0], start[1], 0)])
        while dq:
            x, y, d = dq.popleft()
            nd = d + 1
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    c = (nx, ny)
                    if c in seen or c in extra_walls:
                        continue
                    ft = free_time.get(c)
                    if ft is not None and nd < ft:
                        continue
                    seen.add(c)
                    cnt += 1
                    dq.append((nx, ny, nd))
        return cnt

    # ---- food target ----
    dist_me = bfs_dist(head)
    dmin = None
    for f in foods:
        if f in dist_me:
            dd = dist_me[f]
            if dmin is None or dd < dmin:
                dmin = dd

    target = None
    best_cost = None
    for f in foods:
        if f in dist_me:
            dm = dist_me[f]
            contesters = 0
            if my_health >= 30:
                for oh, _on, _ol in opp_info:
                    if abs(oh[0] - f[0]) + abs(oh[1] - f[1]) < dm:
                        contesters += 1
            if n_opp == 1:
                cost = dm + (2 if contesters else 0)
            else:
                cost = dm + 2 * min(contesters, 3)
        else:
            cost = 150 + abs(head[0] - f[0]) + abs(head[1] - f[1])
        if f == _prev_target:
            cost -= 1.5
        if best_cost is None or cost < best_cost:
            best_cost = cost
            target = f
    _prev_target = target
    field_t = bfs_dist(target) if target is not None else None

    # ---- weights ----
    turns_left = maxt - turn + 1
    max_olen = 0
    for _oh, _on, ol in opp_info:
        if ol > max_olen:
            max_olen = ol
    safe_to_end = my_health > turns_left + 1
    can_coast = my_health > turns_left + 5

    starving = (not safe_to_end) and (
        (dmin is not None and my_health <= dmin + 6)
        or (dmin is None and my_health < 30))
    certain = (not safe_to_end) and (
        (dmin is not None and my_health <= dmin + 1) or my_health <= 3)

    if my_health > 85:
        fw, hpen = 1.8, 500.0
    elif my_health > 50:
        fw, hpen = 2.5, 500.0
    elif my_health > 30:
        fw, hpen = 4.0, 420.0
    else:
        fw, hpen = 6.5, 320.0
    eq_pen = 140.0 if n_opp == 1 else 500.0
    if can_coast:
        if L >= max_olen:
            fw, hpen, eq_pen = 0.8, 900.0, 800.0
        else:
            fw, hpen = 2.0, 650.0
    if starving:
        fw = max(fw, 8.0)
        if n_opp == 1:
            hpen = min(hpen, 150.0)
            eq_pen = min(eq_pen, 110.0)
        else:
            hpen = min(hpen, 250.0)
    if certain:
        fw = max(fw, 9.0)
        hpen = min(hpen, 70.0)
        if n_opp == 1:
            eq_pen = min(eq_pen, 60.0)
    trap_pen = 40.0
    if starving:
        trap_pen = 16.0
    if certain:
        trap_pen = 6.0
    area_cap = (w * h) // 3 + 10

    # ---- squeeze (single opponent) ----
    squeeze_k = 0.0
    opp_head = None
    opp_base = 0
    if n_opp == 1:
        oh, _on, ol = opp_info[0]
        opp_head = oh
        opp_base = flood(oh, {oh})
        if not can_coast and my_health > 35:
            squeeze_k = 2.0 if L > ol + 1 else 0.4

    # ---- candidates ----
    straight = None
    if L > 1 and head != neck:
        v = (head[0] - neck[0], head[1] - neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == v:
                straight = name
                break

    cands = []
    for name, dx, dy in DIRS:
        nh = (head[0] + dx, head[1] + dy)
        if nh == neck:
            continue
        if not (0 <= nh[0] < w and 0 <= nh[1] < h):
            continue
        if nh in blocked:
            continue
        cands.append((name, nh))

    if not cands:
        names = []
        if straight is not None:
            names.append(straight)
        for n, _dx, _dy in DIRS:
            if n != straight:
                names.append(n)
        for n in names:
            for dn, dx, dy in DIRS:
                if dn == n:
                    nh = (head[0] + dx, head[1] + dy)
                    if nh != neck and 0 <= nh[0] < w and 0 <= nh[1] < h:
                        return n
        return random.choice(VALID)

    best_score = None
    best_name = None
    for name, nh in cands:
        score = 0.0
        for oh, on, ol in opp_info:
            if abs(oh[0] - nh[0]) + abs(oh[1] - nh[1]) == 1 and nh != on:
                if ol > L:
                    score -= hpen
                elif ol == L:
                    score -= min(eq_pen, hpen)
        area = flood(nh, {nh})
        if area <= L + 1:
            score -= (L + 2 - area) * trap_pen
        score += min(area, area_cap) * 1.2
        if field_t is not None:
            fd = field_t.get(nh)
            if fd is None:
                fd = 60 + abs(nh[0] - target[0]) + abs(nh[1] - target[1])
            score -= fd * fw
        for oh, on, ol in opp_info:
            md = abs(oh[0] - nh[0]) + abs(oh[1] - nh[1])
            if md == 1:
                if ol >= L:
                    score -= 20.0
                else:
                    score += 2.0
            elif md == 2 and ol > L:
                score -= 4.0
        if squeeze_k > 0:
            a2 = flood(opp_head, {opp_head, nh})
            gain = opp_base - a2
            if gain > 0:
                score += min(gain, 60) * squeeze_k
        if name == straight:
            score += 0.15
        score += random.random() * 0.3
        if best_score is None or score > best_score:
            best_score = score
            best_name = name
    return best_name
```

Hmm wait — bug in candidates: `if nh == neck: continue` — when neck == (-99,-99) fine. But when head == neck (stacked, L=3): neck = my_body[1] = head — nh never equals head ✓.

Hmm, another check — `_prev_target` may hold a food that was eaten; next turn f == _prev_target fails → new target ✓.

Check `starving` when dmin is None and my_health < 30 and not safe_to_end ✓.

One more think about `certain` interplay with can_coast — can_coast implies safe_to_end → starving/certain False ✓ (they check safe_to_end).

Check `field_t.get(nh)` — field BFS includes cells reachable from target going through non-blocked; symmetric ✓.

I think there may be one more subtle issue: `bfs_dist(target)` — BFS from target — but if target is not reachable from my candidates due to MY OWN BODY... field includes paths through my body? My body cells are blocked (in `blocked`) → paths around. OK.

Now, potential issue in 1v1 squeeze: `opp_base = flood(oh, {oh})` — but flood counts cells that free up INCLUDING MY BODY cells (stall 1) — their space includes eventually passing through my body — overestimate for both base and a2 — difference still meaningful. OK.

Also `squeeze_k=0.4` when not longer — mild pressure. Hmm, when I'm SHORTER, pressuring them is risky... 0.4 small. OK.

Double-check `min(gain, 60) * squeeze_k` — max 120 (k=2). ✓

One more: should squeeze be disabled when starving? squeeze flood cost is fine; gain reward might distract from beeline food when starving. Add condition: squeeze_k only if not starving:

```python
        if not can_coast and my_health > 35 and not starving:
```

Good.

Also — the proximity penalty (+2 for smaller snakes adjacent): in 1v1 when I'm longer, +2 near their head encourages contesting — fine.

Final check of variable shadowing: in squeeze block I use `oh, _on, ol` — `ol` shadows nothing later (loop vars re-defined in scoring loops). `opp_head` set. OK.

In scoring, `for oh, on, ol in opp_info` — `on` unused there except in risk loop (`nh != on`). ✓

Syntax: `for oh, _on, _ol in opp_info` fine.

I believe the code is correct. One more pass for dumb bugs:

- `DIRS` tuple of tuples; `order.sort(key=lambda d: d[0] != straight)` — d[0] is name ✓.
- In `_fallback`, `blocked` for stacked body [c,c,c]: body[:-1] = {c}; dup → add c. blocked={c} ✓.
- `decide` → `_decide` returns `best_name` (string) ✓.

Let me trace one more full scenario mentally — 1v1 midgame:
me: head (7,7), body [(7,7),(7,8),(7,8)] wait dup means I just ate. L=3, health 100. opp: head (3,3), len 5. foods [(2,2),(12,9),(7,7)?? no—food can't be under my head. (10,10),(0,14)].
blocked: mine: (7,7),(7,8) + dup tail (7,8) → {(7,7),(7,8)}. opp: (3,3),(3,4),(3,5),(3,6) + tail (3,6) if dup... say (3,3),(3,4),(3,5) no dup → blocked includes (3,3),(3,4) (i<sl-1: indices 0,1) — wait opp len 5, body [(3,3),(3,4),(3,5),(3,6),(3,7)]: blocked: indices 0..3 → (3,3),(3,4),(3,5),(3,6); tail (3,7) free.
Candidates from (7,7): up (7,6), down (7,8)?? down = (7,8) — my neck → excluded ✓. left (6,7), right (8,7). Three candidates.
dist_me from head: fine. Target: nearest uncontested food. field_t from target. Flood areas: large. Scores: fd differences → move toward target. ✓

Now — WAIT, one thing about my `blocked` for MY body with dup tail: body [(7,7),(7,8),(7,8)]: i=0: blocked (7,7); i=1: i<sl-1? 1<2 ✓ blocked (7,8); i=2: dup → blocked (7,8). ✓ Tail cell stays occupied this turn (correct: I just ate, tail doesn't move this turn).

Hmm — wait, is that right?? Body [(7,7),(7,8),(7,8)] — dup tail means I ate LAST turn; THIS turn my tail doesn't move. So cell (7,8) (the dup) remains occupied → correct, blocked ✓. And my head can't reverse into (7,8) ✓.

free_time: my cells: (7,7): t = 3-1-0+1 = 3; (7,8): min(3-1-1+1=2, 3-1-2+1=2)=2. OK.

Alright. One more paranoia: the scoring loop calls `flood(nh, {nh})` — for nh cells... fine.

Also — realize potential issue: in `flood`, extra_walls contains nh, but also should contain... nothing else. OK.

Estimated final answer ready. Let me also double check `state.get("turn")` etc. — judge provides them.

Character count of summary — keep under 300.

Let me write the final response: code block + short summary.

Actually, one more consideration on the risk model: I penalize cells adjacent to equal/longer heads with hpen (500) — but what if the opponent's head CANNOT actually move there because that cell is... they'd die moving there (e.g., nh is their own body... no, nh adjacent to their head can't be their body except neck — excluded via nh==on... their body cells adjacent to their head: only neck is adjacent-adjacent (b[1]). Other body cells are 2+ away (unless stacked L-shape: body b[2] could be adjacent to head! e.g., body [(0,0),(1,0),(1,1)]: head (0,0), b[2]=(1,1) is diagonal... manhattan 2. Snake bodies are connected paths; b[2] can be adjacent to head (a U-turn shape): [(0,0),(1,0),(1,-...)] hmm [(0,0),(1,0),(2,0),(2,1),(1,1),(0,1)]... b[5]=(0,1) adjacent to head (0,0)! If nh = (0,1) (adjacent to their head): they COULD move there (it's their neck-reverse? their neck is b[1]=(1,0); (0,1) is not their neck — valid move for them, though fatal for them (their own body). A suicidal/bad bot might. My drisk penalty applies regardless — fine, conservative.)

Also — should I check "their possible move is fatal FOR THEM" to skip risk? E.g., nh is THEIR body cell adjacent to their head → nh in blocked → not my candidate anyway. nh adjacent to their head but walled for them... they only die if they choose it; they might not know better. Keep penalty regardless — safe.

OK. Also — one more thought about `hpen` magnitude vs `area` for equal-length FFA... done.

FINAL — also ensure no `print` (dropped anyway) — none.

One more potential performance trap: recursion? None. Global mutation fine.

Also, the judge loads bot.py in a new process per game — module-level `_prev_target` resets ✓.

Done. Compose answer.