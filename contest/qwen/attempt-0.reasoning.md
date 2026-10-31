We need answer user wants only python code block plus <=300 Chinese strategy. Need produce strongest bot.py for snake battle. Need think deeply. We need craft code robust, fast, standard library. We don't see judge. Need implement decide(state). Requirements: return direction string. Global variables persist per game. random seeded. CPU limits: load 1s, turn1 1s, later 50ms. Need safe time management. Need algorithm for 15x15 2 snakes and 31x31 11 snakes, up to 500/800 turns. Need maximize survival and length. Rules simultaneous. Need account head-to-head collisions, tail moving unless grew, food simultaneous. Need strategy: avoid immediate death, space/flood fill, food chase, aggression? Need robust. Need perhaps Monte Carlo? Time 50ms per turn. Could implement heuristic + search. Need handle many snakes. Since unknown opponents. Need survive first, length second. Need maybe Hamiltonian cycle? Board sizes small but many snakes. Single opponent 15x15: can use lookahead/minimax? But simultaneous, unknown opponent decide. For robust, use safe move selection with simulations of possible opponent moves? Need rank by expected outcome. Need not overcomplicate causing errors.

Let's parse rules. State gives alive snakes, including self. Body list head first. Length field maybe actual length? Initial body three overlapping same cell. Movement: tail retracts simultaneously; reverse into neck invalid and continue original direction. Need know current direction? Can derive from body if length >1 and head != neck. But initial overlapping: if head equals neck, direction unknown? State turn 1 body likely [[x,y],[x,y],[x,y]], no direction. The referee may have current direction? Not given. If we return opposite of current direction when collapsed? If no neck distinct, reverse invalid? Need choose any. We can track our last direction globally. Since each game new process, decide called each turn. Need maintain own prev direction and previous state maybe. If state turn 1, choose direction. If we choose reverse? There is no current. For collapsed, maybe original direction arbitrary? The rules: open with 3 stacked at spawn, will unfold after few moves. How does initial direction work? If all stacked, moving any direction likely head moves, tail shrink? If length 3 all same, moving one step results body [new, spawn, spawn]? Maybe okay. If we later derive direction from body when not collapsed. Need track last_dir to avoid invalid turn? We can store.

Important collision: head into any body except heads? It says head bumps any snake's body (except snake head arbitrary section, including own): dead. Heads same cell resolved by length. So moving into a cell occupied by another snake's head currently? If both heads move into same cell this turn: head-on collision. If only I move into opponent's current head cell while opponent moves away? Since simultaneous, opponent head leaves, unless it grows? The current head cell becomes empty (if not body behind). But if opponent's head stays? impossible unless reverse invalid? If opponent doesn't move? They must move. So current head cells are not obstacles for next step except if multiple heads? For safety, need simulate next positions. Body cells excluding tails that will move are obstacles. Tail cells are safe unless that snake just ate (tail not move). Detect just ate by last two body positions equal? Example last two overlap. Also if length maybe body has duplicates due initial stack. A snake that ate previous turn: new segment added at tail, so tail doesn't move this upcoming turn. In state body after eating? Example body last two overlap indicates just ate, next turn tail不动. So in simulation, for each snake, tail cell is unsafe if just grew (body[-1]==body[-2])? Also initial 3 stack: they haven't eaten? They start length 3 overlapping; tail should move? The note says like above last two overlap, just ate, next turn tail not move. But initial could also overlap; maybe treated as just ate? It says 3 nodes stacked at birth, walk few steps to unfold. If tail not move initially? Hmm if length 3 all same, body[-1]==body[-2], our heuristic would mark tail stationary, making spawn unsafe. But they likely all stacked and tail maybe doesn't move? Let's reason: If body = [spawn,spawn,spawn], choose direction: head moves to new, tail simultaneously retracts one? Body becomes [new, spawn, spawn]? Length remains 3. Then next turn if move, body [new2,new,spawn]? So unfolded after 2 turns. If tail retracts from spawn, one spawn removed; still two spawn. If tail not move because grew? Then body [new, spawn, spawn, spawn]? length increase? no. The note about last two overlap just ate applies to normal. For initial, if all overlap, perhaps not just ate; but last two overlap true. If we mark tail stationary, for our own safety we might avoid moving into spawn? But we move out. For opponents, their spawn cell might be unsafe for one more turn? Actually if tail doesn't move? Need simulate accurately. Could treat any snake with len(body)>1 and body[-1]==body[-2] as tail staying. For initial all 3 same, tail stays? But then after moving, body length? If tail stays and head moves, length should become 4? But length remains 3? Maybe implementation in judge uses pop(0?) Let's model common snake: body list head to tail. Move: insert new head; if not grow: pop tail. If initial [s,s,s], pop tail -> [new,s,s], okay tail cell s still occupied by two segments. Last two equal but not due grow; next turn if not grow, pop tail -> [new2,new,s]. So tail cell s is still occupied (by last segment) but the specific tail segment moves? The cell s remains occupied because there are two segments there. For collision, we care cells occupied after move. To compute occupied cells next turn, for each snake, current body cells except tail if not growing and length? If body has duplicates, removing one tail duplicate still leaves tail cell occupied by previous segment. So simple set(body[:-1]) if not growing may remove cell even if duplicate remains. Need count? Actually collision only cares if any segment in cell. If tail cell has duplicate, and one tail segment leaves, another remains, so cell remains occupied. For safe simulation, need multiset or know that if body[-1]==body[-2], tail cell remains occupied even if tail moves. The rule for tail safe: tail in step 1 already缩回, so can follow somebody's tail; but just ate tail doesn't move. If body tail duplicates due initial or just ate? For just ate: body example [9,3],[9,4],[9,5],[9,5] length 4. Before eat, length 3? It grew, new segment added at tail, so last two overlap. Next turn tail does not move: body after move [new,9,3],[9,4],[9,5],[9,5]? Actually no pop. Cell 9,5 remains occupied by two segments? If no pop, yes both tail segments remain; but one is new? The cell is occupied. If we use body[:-1] safe? For growing, all body cells remain obstacles (tail not move). For non-growing but duplicate tail, removing last segment still leaves duplicate occupied, so body[:-1] includes body[-2] same cell, so tail cell remains in set. Good! If body=[s,s,s], not growing? body[:-1]=[s,s] includes s, so cell remains. So simply obstacles for next positions = all body cells if tail stays (just grew?) else body[:-1]. But for initial, if not grew, body[:-1] includes s, so still obstacle. Good. But if body length 2 and tail duplicate due just ate? body[:-1] includes head? Need okay.

But can a snake's current head cell be obstacle next turn? If it moves and no segment remains there (unless neck duplicate), it becomes empty. In obstacles body[:-1] includes current head, which would mark current head cell obstacle. But head moves away. Actually body[:-1] includes head and all except tail. That's wrong for next occupancy: The segments that remain in their cells are all body except head? Let's define current body [head, neck, ..., tail]. Move: new head added. Each existing segment shifts forward: head moves to new cell, neck moves to old head, body2 to old neck, ..., tail moves to previous segment if not grow. Thus next occupied cells = {new_head} ∪ current body[:-1] if not grow? Because old tail removed, but old head remains occupied by neck, old neck by next, etc. Yes current head remains occupied by neck unless length 1 (not). So current head cell is obstacle unless no neck? So body[:-1] is correct for non-growing: all cells except tail remain occupied. For growing: all current body remains plus new head, so current body cells obstacles. Good. For duplicates, set okay.

For our own possible move, need ensure new head not in obstacles after movement excluding our own old? Since our neck will occupy old head, so old head is obstacle, but we don't move into it unless reverse (invalid). Other current head cells of opponents: their necks will occupy them, so they remain obstacles if opponents move (unless they die? But immediate next step before elimination? For choosing move, if opponent also moves, their current head cell remains occupied by their neck, so moving into opponent's current head cell is collision unless head-to-head? Suppose opponent head at H, neck at N. They move to H2, neck moves to H. If I move into H, my head enters H, their neck also remains H (not a head). Rule: head collides with body (except heads). Their neck is body, so I die. If both heads enter same new cell, head-on resolved. So current head cells are obstacles (occupied by neck) except if opponent length? If length 1? no. If opponent just grew? still. So obstacles for next step from other snakes = body[:-1] if tail moves, body if tail stays. That includes current head. Good. For our own body obstacles = body[:-1] if not grow else body; but we can't move into own body except maybe tail if moving and tail cell vacates and no duplicate. Our body[:-1] excludes tail, so moving into tail safe if not growing and no duplicate. If body[-1]==body[-2], body[:-1] includes tail cell, unsafe. Good.

Need account head-to-head: If our new head equals another snake's new head. We don't know their move. For immediate safety, consider possible enemy moves. Conservative: any adjacent cell to enemy head could be their new head. If we move into adjacent cell, may head-on. If we are shorter/equal, bad; if longer, we win. But enemies can choose. Need heuristic.

We need produce strongest possible within one response. Could implement layered decision:
1. Parse state, identify self.
2. Determine possible directions not reverse? If reverse invalid, we can still return but will continue original; better avoid. Need know current direction. Use global last_dir. But state may not correspond? Need robust derive.
3. Generate candidate moves that are not immediately fatal assuming worst-case? Need choose best by evaluation.

Potential approaches:
- Use game tree search with deterministic assumptions: model opponents choose moves greedily? Too heavy for 11 snakes 31x31. Could do 1-ply or 2-ply Monte Carlo random opponents, evaluate survival. But 50ms, Python. Maybe okay for small depth? Need fast.
- Use Hamiltonian cycle on 15x15? In single duel, if we can survive long, but food competition. Hamiltonian cycle guarantees not collide self, but opponents can collide with us? If we follow cycle, opponents may run into us and die, good; but if they occupy cycle cell ahead? Since we move along cycle, if an opponent body is on next cell, we die. Need avoid dynamic obstacles. Could use safe tail-chasing / space. But Hamiltonian with obstacles not simple.
- Strong general bot: choose move maximizing (survival probability under random opponent moves, flood fill space, distance to food, aggression). Could be enough.

Need consider scoring: Bradley-Terry pairwise. Need win both formats. Survival most important. In time limit, if many die, last survivor wins. In 11 snakes, early chaos. Need avoid heads and bodies. Likely many bots die quickly. Conservative survival may rank high. But need eat to grow and avoid starvation. Health 100, board has enough food. In 31x31 with 11 snakes, food 12. Need path to food but avoid crowded areas. In single duel, need outplay one opponent. Could use more aggressive search.

Let's design robust bot with modes:
- Maintain global last_state, my_id, last_dir, maybe history.
- At decide, if first turn choose direction perhaps toward center/food? For spawn positions, avoid walls. For 15x15 single: (3,3) and (11,11). Choose toward center? For (3,3), down/right. For brawl spawns around circle, choose inward? Could compute direction toward board center or nearest food, avoiding wall.

Need ensure return valid string always. Wrap all in try/except fallback.

Core algorithm idea:
For each legal direction (not reverse if possible), simulate one step with assumptions about opponents. We can compute "immediate safe" under worst-case? Need avoid moves where new head hits static obstacles (walls, bodies that will remain). Also avoid moves where new head is adjacent to enemy head? Actually if enemy can move into same cell, head-on. We can penalize.

Maybe use "danger map": For each enemy, possible next head positions = adjacent cells (including reverse? If reverse invalid, their current dir matters unknown; but we can assume all 4). For each such cell, if my length <= enemy length, moving there risks death; if > enemy length, safe/win. But enemy may not choose it. Use as cost.

Static safe: new head inside and not in occupied_next cells (all snakes body except moving tails) except if new head equals an enemy's current head? occupied_next includes current head due neck. But if enemy moves, current head occupied by neck, so yes unsafe. But wait if enemy dies this turn? We only care our move; if enemy also moves into collision and dies, but their neck remains? The elimination after movement: If I move into enemy's current head cell, enemy neck moves into current head, so two entities? My head and enemy neck same cell. Rule says head collides with any body (except snake head). Enemy neck is body, so I die. Even if enemy head elsewhere. So unsafe. Good.

But tail cell of non-growing snake with no duplicate is safe. Our own tail safe if not just grew. Need compute dynamic obstacles per snake considering tail move and duplicates. For each snake: if body length <=1? not. grow = len(body)>=2 and body[-1]==body[-2]? Also if health? No. If grow then occupied = all body cells. Else occupied = body[:-1] (as set). But as argued for duplicate tail non-grow initial, body[:-1] still includes tail cell. Good. For own, if we choose move and not eating, our tail moves, but our old body[:-1] obstacles; new head cannot be in that. That excludes neck etc. Moving into current tail if unique safe because excluded. Good.

Food: if new head on food, we grow, so our own tail doesn't move this turn. Does that affect whether new head can be current tail? If new head is food and also our current tail? Can't happen because tail cell occupied by body and food spawns only empty cells? Food may be on tail? Rules food appears random empty? likely empty. But if tail cell has food? Not. For obstacle computation for our move if we will eat: our existing body all obstacles; new head cannot be any current body cell. If new head is food not body. So safe.

But static obstacle set should include all snakes' current bodies except tails that will move. For self if we will eat, tail won't move; but new head not tail anyway. For simplicity, use body if last two overlap else body[:-1] for all snakes. But for self, if new head is food and last two not overlap, tail moves; but our own body[:-1] still obstacles. Good.

However, if an enemy's tail is unique and will move, their tail cell is safe for us to move into, but if we both move into same tail cell? Enemy tail moves out, but enemy new head may be elsewhere. If another snake's head also moves there, head-on. We can ignore or penalize. Following tail safe.

Need pathfinding / flood fill. For each candidate move, compute accessible space after move using flood fill over cells not occupied by bodies that will remain (maybe with tails safe). Need include our own new body? For future space, after move, our body occupies new_head + old body[:-1] (if not grow) or old body (if grow). Other snakes unknown. Could approximate obstacles as current bodies with moving tails. Flood fill from new head counting reachable empty cells, maybe with tail cells considered empty. Space important.

Need food targeting: choose nearest food by BFS distance considering static obstacles? Need avoid path through unsafe cells. Compute BFS from my head to foods on grid with obstacles = occupied cells except moving tails maybe. But need ensure path safety dynamic not guaranteed. Use distance as tie-break.

Need head-to-head avoidance: In candidate scoring, if new head adjacent to enemy head? Actually if enemy head can move into new head. For each enemy, if new_head is one step away from enemy head (Manhattan 1), possible head-on. If my length <= enemy length, high penalty; if > enemy length, maybe okay but still risky if multiple. If new_head equals enemy head? Static unsafe (occupied by neck) so excluded. If new_head is two steps? no immediate.

Also enemy could move into cell adjacent to us causing threat next turn. Hard.

Maybe implement 1-step lookahead with opponent response: For each my move, consider all possible enemy moves (or top greedy) and evaluate if I survive after enemy moves? But many snakes. For single duel, can do deeper minimax? Let's think.

Single duel 15x15, 2 snakes, 500 turns. Strongest could use game tree search with simultaneous moves. Since opponent unknown, we can model them as choosing moves that minimize our expected utility. Could do minimax with depth maybe 4-6? Branching 4 each, 16 combos per ply. But state transitions with collisions. Need evaluate space/length. 50ms, depth 4 maybe 16^2? Actually simultaneous plies: my moves 4, opp responses 4 => 16 states. Depth 2 => 16^2=256, depth3=4096, maybe okay in Python with optimized bitsets? 15x15 small. But opponent's objective includes their survival, not purely zero-sum? Pairwise ranking: if both die same turn, length decides. We can use utility: (my death turn, my length) vs opponent. But in pairwise, winning means survive longer or longer if same. Zero-sum-ish. Could do minimax assuming opponent tries to maximize its own outcome. But they are actual bots not optimal. Still robust.

For brawl 11 snakes, search impossible. Use heuristic.

Could detect num_snakes==2 and width==15 for duel, use more aggressive search. But code complexity. Need ensure no bugs. Maybe simpler heuristic enough? But want strongest. Let's explore potential algorithms.

Possible state representation for fast search:
- Board dimensions <=31x31 (961 cells). Use integer indices y*w+x.
- Bodies as tuples/lists of ints. Need simulate moves for all snakes. For heuristic evaluation, maybe not full search.

Could implement a generic move scorer with multiple features and random tie-break. This may be stable.

Features:
- immediate_death: 0/1 (static collision/wall). Exclude.
- head_collision_risk: possible enemy heads. If risk and length <= enemy length, heavy penalty. If length > enemy length, smaller.
- space: flood fill count from new head after assuming my move and all snakes tails move. Count reachable cells up to limit maybe area. More space better.
- tail safety: distance to own tail? Maybe if no food, chase tail to survive.
- food distance: BFS shortest path to nearest food on safe grid. Prefer closer, but if path length > health? health 100; not issue if within 100. Actually hunger: health decreases each turn; if no food within 100 turns die. Need ensure reachable food within health. In large board with 12 food, likely. Use dist to food.
- centrality: prefer away from walls? Maybe space covers.
- aggression: if enemy head adjacent and we longer, move to cut? Could be risky.
- avoid being adjacent to enemy head? Maybe.

Need decide under time. Could compute BFS distances from candidate head to foods and space. For 31x31 and 4 candidates, BFS okay. 50ms? Python BFS over 961 cells * few = okay.

But heuristic may be mediocre. Could incorporate "survival tree" for candidate moves: simulate random opponent moves for N plies (Monte Carlo) and estimate survival. But random may not model strong opponents. Could use adversary random? Maybe sample. Time 50ms, for brawl maybe 50 simulations of depth 8? Could be okay if optimized? Need standard library only. But randomness seeded. Could use random module. However Monte Carlo with random opponents may choose suicidal moves; not strong. Could restrict opponents to non-immediate-death moves. That gives survival against chaos. But strong opponents target us? Could incorporate adversarial: for each my move, choose enemy moves that minimize my safety? Too many.

Alternative: compute "danger zone" of enemies: cells that enemies can reach sooner than me? Use Voronoi. For food chasing, avoid contested food. Could compute BFS distances from my head and all enemy heads to each cell (with obstacles). Choose food where my distance < enemy distance. This is strong. For single duel, important to claim food. For brawl, avoid fights.

We can compute multi-source BFS distances from enemies (min steps) on current obstacles (treat moving tails as empty?). Then for candidate moves/foods, prefer cells where my_dist < enemy_dist (safe ownership). But dynamic bodies complicated.

Maybe implement path planning to a target chosen by scoring foods:
For each food, compute BFS distance from my head ignoring moving tails? obstacles = static bodies except tails. Also compute enemy_min_dist to food. Score food = -my_dist + (enemy_dist - my_dist)*bonus - risk. Choose target food with my_dist < enemy_dist maybe. If none safe, choose safe wander / tail chase.

Then choose move along shortest path to target that is immediate safe and maximizes space. If no path, choose move maximizing space.

Need avoid traps: flood fill after move. Could also compute "reachable food count" within health? Maybe.

Could implement "tail-following" when no safe food: target own tail (or a safe cell near tail) to maintain space. Since tail moves, chasing tail can survive.

Need handle initial overlapping direction: derive last_dir. At turn 1, no previous. Choose direction to center/food. Need store last_dir. If state changes? We can update last_dir to returned direction if not reverse? But if reverse invalid, actual direction remains previous. Need know if our chosen direction is opposite of current direction; if so, actual direction is previous. But we can avoid returning reverse. For initial, any.

Need know current actual direction from body: If len(body)>1 and body[0]!=body[1], vector head - neck. If equal, use last_dir. If last_dir None, choose. For reverse check: opposite of current_dir invalid. But if body collapsed and last_dir None, no reverse. If we choose a direction, set last_dir=chosen? If actual may be different due invalid? We'll avoid invalid.

But if we are forced fallback, maybe return last_dir or 'up'. Need robust.

Potential bug: state['snakes'] includes length field maybe not equal len(body)? Use len(body) for collision? Length for head-on uses official length; could use s['length'] if present. Body may have duplicates; len(body) probably length. Use length = s.get('length', len(body)). But for just grew detection, last two overlap.

Need global variables to cache? Since decide called each turn, can store previous state to detect if we ate? Not needed.

Time management: Use time.process_time? CPU time. import time. For each turn, set deadline = now + 0.045 (leave margin). For turn 1 maybe 0.9. If exceed, fallback to quick safe move. But functions should check. Could implement simple. Since Python overhead. Need avoid infinite BFS. Use limits.

Could have two modes: duel_search if num_snakes==2 and small; else heuristic. But maybe code length large. Need ensure correctness. Let's design a solid heuristic with optional shallow lookahead.

Detailed move scoring generic:
Input state -> my snake, enemies, food.
Preprocess:
- w,h
- idx(x,y)=y*w+x
- directions list with dx,dy, name.
- my_body = list of idx, head idx.
- current_dir = derive from my_body or last_dir.
- legal_dirs: all dirs except opposite current_dir (if known). But if all illegal? include all.
- For each snake, compute body_idx list. Determine tail_stays = len(body)>=2 and body[-1]==body[-2] (maybe also if length > len? but). For obstacles_current_next: set of cells occupied after movement excluding new heads? For static collision for my new head, for each snake: if snake is me? We'll handle separately. For other snakes: if tail_stays: add all body cells; else add all body[:-1]. This marks cells that will be occupied by their bodies after they move (excluding their new heads). For own: if I don't eat, obstacles = my_body[:-1]; if eat, my_body. But whether I eat depends new_head in food. For candidate, use own_body_except_tail if not food else full body.
But for flood fill after my move, need obstacles including my new body and maybe other snakes' next bodies? Approximate using current bodies with tails moved. We can make grid blocked = occupied_next for all snakes except maybe my old tail? Then after my move, set my new head blocked? For reachable space from new head, we should treat new head as start, and blocked cells = other snakes' occupied_next + my new body (old body except tail plus new head). But old body cells are blocked; reachable excludes them. For space, count empty cells reachable from new head after moving, not through blocked. Need include moving tails as empty (if tail_stays false). For other snakes, their new heads unknown; we can ignore or treat adjacent to heads as danger but not blocked.

Candidate immediate safe:
- new cell inside.
- not in blocked_for_candidate: other_occupied_next + own_occupied (depending eat).
But head-on: if new cell equals possible enemy new head. We'll score not hard exclude unless certain? If enemy has no other safe moves and must move into us? Hard. Could treat as risk.

Potential issue: If two heads currently adjacent and both move into each other's current head? That would be swapping? Is that allowed? Suppose my head A, enemy head B adjacent. I move to B, enemy moves to A. After move, my head at B, enemy neck at B? Wait enemy's neck occupies B (old head) because body shifts. So my head collides with enemy neck at B, die. Enemy head at A, my neck at A, enemy dies. Both die? So swapping heads is fatal for both due necks. Our static obstacle includes enemy current head B, so we exclude. Good.

If enemy current head B and tail? okay.

Compute enemy_possible_heads: for each enemy, adjacent cells inside not blocked by their own body? Could compute legal enemy moves (not reverse? unknown). For risk, any adjacent inside. If new_head in enemy_possible_heads:
- if my_length <= enemy_length: high penalty (likely death if they choose). Maybe if cell is also their only move? uncertain. Could exclude if length<=enemy and enemy distance 1? But sometimes necessary. Use strong penalty rather than hard, unless all candidates risky choose least.
- if my_length > enemy_length: small penalty or maybe beneficial? Head-on we win, but if multiple? They might avoid. But moving into adjacent cell could kill them if they choose; not reliable.

Also if new_head adjacent to enemy head (Manhattan 1) but not necessarily same as possible? Actually possible head positions are exactly adjacent. So same.

Need head-to-head with multiple enemies: if two enemies could move into same cell and I also, if I longest maybe survive? Complex. Penalize max.

Flood fill/space:
Function reachable_count(start, blocked, limit maybe w*h). Use deque. Count start if not blocked. But start is new head; blocked includes old body but not start unless start in old body (would be unsafe). Count cells. Also can incorporate danger: avoid cells adjacent to enemy heads? Maybe not for space.

We need evaluate space after several turns? Flood fill current may overestimate because enemy heads move into space. Could compute "safe space" excluding cells within 1 of enemy heads? Maybe too conservative. Use distance to enemies.

Food path:
Compute BFS distances from my head on grid blocked by current obstacles (other occupied_next? and own body except head?) to each food. But my head moves; for candidate, we can just use distance from new_head to food with blocked after move. For scoring maybe global target.

Simpler: For each candidate, compute nearest food distance from new_head using BFS on blocked grid after move (with my new body). Choose min distance. If no reachable, large. Prefer smaller. But BFS per candidate per turn over 961 cells okay. 4 BFS for space + food maybe heavy but fine 50ms? Need optimize. Could compute one BFS from new_head that yields distances to foods and count reachable within limit. For each candidate, BFS until all reachable or limit. For 31x31, 4*961 ~ 3844 cells, okay. In Python maybe <5ms. Additional enemy BFS maybe.

But path to food must consider that obstacles move. Approximation okay.

Need health urgency: If health low (<40), weight food more. If health high, space more.

Scoring formula:
score = -100000 if immediate unsafe
else:
 score += space * 10 (or log)
 score -= food_dist * food_weight
 score -= head_risk * risk_weight
 score += centrality small
 score += enemy proximity? maybe avoid.
 choose max.

Need tune. Could do lexicographic: first survival (no immediate death, no high head risk), then space, then food. But if all safe, choose. We can create tuple:
( survive_rank, -risk, space, -food_dist, centrality)
But risk continuous.

Maybe use thresholds:
- If candidate has head_risk_fatal (enemy possible head and my length <= enemy length), mark danger. If there is any candidate without fatal risk, exclude fatal unless all fatal. But sometimes moving into risk is only way to food. Still avoid if possible.
- Among safe, maximize space, then food.

But strong opponents may exploit if we always avoid risk and starve? Health 100, enough food. In brawl, survival key.

Could implement "ownership" BFS to choose target: Avoid food closer to enemies. But candidate scoring with food_dist may send into contested area. Add enemy_dist_food. Compute enemy_min_dist to each food via BFS from all enemy heads (or possible next heads). Then for candidate nearest food, if my_dist >= enemy_dist, increase penalty. Could compute per candidate BFS distances to food and compare to precomputed enemy distances. Enemy BFS obstacles? Use same blocked grid? Multi-source from enemy heads. Could approximate.

Let's design more systematically.

State preprocessing:
- cells = w*h
- direction maps.
- my snake object.
- snake_infos: for each alive snake: id, body list idx, length, head, tail_stays, occupied_next (set/list bool array), possible_next_heads (list idx) maybe.

Occupancy representation: Since board <=961, use Python int bitsets for speed? Could implement blocked as list of booleans or int bitmask. Bitsets can speed flood fill? Maybe simpler with lists. 50ms okay. But code robustness. Use bytearray for blocked. For BFS, use list/bytearray visited.

Need be careful with using sets vs lists. For 31x31, sets okay but maybe slower. Could use bytearray length cells. Build occupancy arrays:
- static_block_others = bytearray(cells): cells occupied by other snakes after tail move (excluding their new heads). For each enemy: if tail_stays: mark all body; else mark body[:-1].
- For self candidate: own_block_base = bytearray? We can compute own_body_except_tail mask once, own_full mask. For candidate if new_head in food: blocked_self = own_full else own_body_except_tail. But own_body_except_tail should exclude tail if tail moves. However if tail duplicate, body[:-1] includes tail cell; okay. Need mark own old head? yes. If moving, old head occupied by neck, blocked. If initial collapsed, body[:-1] includes head cell etc. Good.
- For candidate immediate blocked = static_block_others OR blocked_self. If new_head blocked -> unsafe. But if new_head equals own tail and tail moves and no duplicate, not blocked. Good.
- What if new_head equals an enemy tail that moves and no duplicate: not in static_block_others, safe. But if enemy just grew, blocked.

Need also walls. Check coordinates.

Head risk:
For each enemy, possible_next_heads: adjacent cells to enemy head that are inside and not blocked by enemy's own occupied_next? Actually enemy can't move into its own body (except tail if moving) and wall. Reverse invalid maybe but unknown. For risk, consider all adjacent inside that are not in enemy's own blocked (body except tail if tail moves). But if cell is blocked by another snake body, enemy would die if moving there; but could still? Strong opponents avoid. For worst-case, maybe include all adjacent inside. But too conservative. Use legal-ish: not blocked by occupancy of all snakes? If enemy moves into a static occupied cell, they die, but if they are desperate maybe. To assess risk to me, if enemy can move into new_head and survive? Need new_head not blocked for them. If new_head is my new head, obviously head-on. If new_head also occupied by body? If it's a body cell, I wouldn't be there if unsafe. For enemy legal moves, new_head should not be blocked by other bodies (excluding heads?) Hard. We can simply consider adjacent cells inside. Penalize.

Maybe compute enemy_threat[new_head] = max over enemies if Manhattan(head_e, new_head)==1. If my_len <= enemy_len: fatal_risk += 1; else win_risk +=1. But if enemy head is adjacent but its path to new_head is blocked by its own neck? For adjacent cell could be its neck (reverse) invalid. Example enemy body head H, neck N. Cell N is adjacent; moving into N is reverse invalid, so not possible. We can derive enemy current direction if body distinct; exclude opposite. But enemy may be collapsed. Use possible directions not reverse based on derived direction. For each enemy, current_dir from body if possible else unknown all. Possible heads = H + d for d in dirs except opposite current_dir, inside, and not in enemy's own occupied_next? Actually moving into own body (excluding tail if moves) fatal. Use own_block for enemy: if tail_stays: body all; else body[:-1]. If candidate cell not in that, possible. But if cell is own tail unique, possible. Good. This reduces false risk. For head-on risk, if my new_head in enemy_possible_heads. Note: if my new_head equals enemy head? not adjacent, static blocked. Good.

Also if multiple enemies could head into same cell, risk. If we are longer than all, maybe safe. If equal/shorter, fatal. If equal and both die, ranking? If both die same turn, longer length wins; equal length both die tie? In pairwise, if both die same turn same length maybe tie? But we want avoid.

Could hard exclude fatal_risk if alternatives. But if enemy is behind us and possible head cell is where we need to go? If adjacent enemy, moving away may not be fatal risk unless enemy moves into our new cell. If we move into cell adjacent to enemy head, they could chase. Many moves will be adjacent to enemy if close. Hard exclude could leave no move. Use scoring.

Space calculation with danger? We can count reachable cells that are not "fatal risk cells"? For future, maybe. Could compute reachable cells using BFS over blocked, but also avoid cells with enemy_possible_head fatal? If we count them, overestimate. Maybe mark as blocked for space if fatal risk? But enemies move, risk changes. Could mark cells adjacent to enemy heads where we are not longer as danger and not count or higher cost. For space, count reachable safe cells (excluding danger). But if danger cells are only passage, maybe still need. Could count all but penalize candidate if new head danger.

Maybe implement two flood fills: reachable_total and reachable_safe (not danger). Use safe_space for scoring. But if safe_space zero, use total.

Food BFS should avoid danger? Could use blocked + danger (fatal) to find safe path. If no safe food, use total.

Target selection: Instead of candidate BFS food distance, compute BFS from my head to foods with blocked/danger? But we need choose move. Could choose target cell (food or safe wander) and then move along path. Simpler candidate scoring with BFS from each candidate.

Let's think of strong single-duel behavior. Heuristic may lose to aggressive search. Could implement specialized duel minimax? Let's explore feasibility and design.

Duel minimax/expectimax:
State: two snakes, food. Need choose my direction. Opponent unknown. We can assume opponent chooses among legal moves with some policy: perhaps greedy to maximize its own heuristic (survival, food, space). We can simulate one or two plies and choose move that leads to best outcome against worst-case or expected. Could improve. But risk of bugs. Maybe use "MCTS" random opponent not strong. Heuristic may be safer.

Could implement "survival oracle" for myself: choose move that maximizes number of turns I can survive assuming opponents are obstacles moving randomly? Not enough.

Maybe implement known strong strategy for Snake battle: Use A* to food with safety check (after eating, can reach tail). In classic snake, choose path to food if after simulated path you can still reach tail; else chase tail. For multiple snakes, treat others as obstacles. This is strong. Since health 100, need food. For single duel, if we can path to food safely and preserve tail reachability, good. For multi, similar but avoid opponents.

Classic algorithm:
- Represent obstacles as snake bodies (with moving tails maybe safe). Find shortest path to nearest food.
- Simulate moving along that path (assuming food eaten) to update snake body, then check if head can reach tail (or a safe space) via BFS. If yes, take first step.
- Else, choose move that maximizes space or chases tail.
This can be powerful. Need adapt to multiple moving snakes and simultaneous collisions. Could do per turn: compute path to best food using BFS on current blocked (treat other tails safe? maybe). Then validate first step by flood fill / tail reachability. But other snakes move, may invalidate.

Tail reachability for self: Since own tail moves each turn unless ate, if we can reach our tail, we can survive (in static empty board). With opponents, not guaranteed. But good.

Maybe implement move selection:
1. Generate immediate safe moves (not wall/body, low head risk).
2. For each, compute space_after (flood fill) and distance to nearest food after move, and tail reachable after move? (Can new head reach own new tail?). Choose move with tail reachable and good food/space.

Need simulate own body after candidate:
- new_body = [new_head] + my_body[:-1] if not eating else [new_head]+my_body. But if not eating and body duplicates, pop last. If length initial, okay. For tail reachability, target tail = new_body[-1]. But if tail cell occupied by body? If duplicate, tail cell has multiple segments; reaching it? In snake, chasing tail cell when duplicate maybe unsafe because tail not moving? If just ate, tail stays, cannot reach? For survival, target should be cell that will be vacated. For simplicity, if new_body[-1]==new_body[-2] (tail stationary), tail reachability less meaningful. Could target adjacent safe cell.

Classic safety check: after move, BFS from new head over cells not occupied by new_body[:-1]? Tail cell allowed if tail will move next turn (unless just ate). If BFS can reach tail cell, safe. For multiple snakes, include other obstacles. But if we just ate, tail doesn't move, so reaching tail cell impossible/unsafe; need space.

Could implement tail_reachable_after_move(candidate): Build blocked after move: other static obstacles? my new body except tail if tail moves, full if tail stays. BFS from new_head; see if tail cell reachable (if tail moves and not duplicate? Actually if tail moves next turn, tail cell will be empty, so can move into it next turn; BFS target tail cell). If tail_stays (new_body last two equal), target not tail but any cell? Maybe require space >= length.

But other snakes' future positions unknown. We can treat their current occupied_next as obstacles.

Food path safety: Could choose food if after moving one step toward it, tail reachable. But need full path simulation to ensure can eat before opponents? Maybe too much.

Alternative: Use "best move by scoring with BFS space and tail reachable".

Let's outline robust code:
Global:
```
last_dir = None
last_head = None
last_turn = None
```
Derive current direction:
```
def get_dir(body):
 if len(body)>=2 and body[0]!=body[1]: return direction from body[1] to body[0]
 return last_dir
```
But body coords lists. Convert to idx maybe.

decide(state):
```
try:
  return decide_main(state)
except Exception:
  return fallback()
```
Need fallback uses last_dir or safe from state minimal.

Because exceptions could hide bugs; fallback should return valid direction. But if fallback itself error? Use 'up'. But if up invalid? The judge will continue original if invalid? Returning invalid string causes original direction. Better return last_dir or 'up'. If process new, last_dir None. okay.

Time: At start `start = time.process_time(); limit = 0.9 if turn==1 else 0.045; deadline = start+limit*0.8`. Pass deadline to functions; if near, return best so far.

Need maybe use random for tie-break. Since random seeded. Use small random shuffle of equal scores. But deterministic maybe okay. Could use random.random tie.

Now, to maximize strength, maybe implement two-tier: For 2-player 15x15, use a lookahead simulation with candidate moves and opponent policies. Let's consider adding a simple adversarial 1-ply/2-ply evaluation on top of heuristic.

Since 15x15 small, we can evaluate each my candidate by simulating opponent's possible moves (legal) and taking worst-case or expected of resulting immediate survival/space. For each my move, for each enemy move (4), compute next state (two snakes), check if I die, enemy dies, lengths, then evaluate space/food. Choose my move maximizing min or expected. This accounts head-on and cuts. Could improve. But if we assume worst-case, may be too defensive. Could use a mix: worst-case for immediate death, heuristic for rest.

For 11 snakes, too many combos. Could still simulate each enemy independently? Not.

Maybe implement generic "opponent modeling": For each candidate my move, compute a "threat score" by considering each enemy's best response (greedy) one step. For each enemy, choose enemy move that maximizes its own heuristic (food/survival) or minimizes mine? Then update. But not necessary.

Let's focus on a high-quality heuristic with safety.

Important: The ranking prioritizes survival time, then length. If we die because starvation while avoiding risks, bad. Need eat enough. Health 100: we can survive 100 turns without food. Max turns 500/800. Need eat periodically. In 15x15 with 3 food, average distance small. In 31x31 with 12 food, distance moderate. So can afford be safe.

Potential failure: Flood fill overestimates because treats enemy tails safe, but enemy bodies move. Could get trapped by opponents. Need avoid enemies' heads, maintain distance. Add "enemy distance penalty": For candidate, compute min Manhattan/BFS distance to any enemy head; prefer larger, unless food. Maybe weight.

Could compute "Voronoi safety": BFS from all enemy heads on blocked grid to get enemy distance map. Then for candidate new_head, if enemy_dist[new_head] <= 1 (adjacent) dangerous; if <= my distance? We can compute my_dist from new head? Hmm. For food target, prefer foods where my BFS distance < enemy distance. For move, prefer cells with enemy_dist > 2.

Let's design full decide_main:
1. Parse state, build Snake objects.
```
class Snake: id, body (list idx), head, length, tail_stays, dir
```
But avoid class overhead? okay.

2. If my snake not found, return 'up'.
3. Determine current_dir. Update global last_head? maybe.
4. Build occupancy masks:
- `occ_others_static = bytearray(cells)` mark cells occupied by other snakes after tail move (tail_stays? all body : body[:-1]). Also maybe include food? no.
- `enemy_possible_heads = bytearray(cells)` or list of sets with length info. For each enemy, possible moves based on current_dir and own body. Mark possible head cells; also store max length? For fatal risk, need if any possible enemy length >= my_length. We can create `danger_head_fatal = bytearray(cells)` where enemy possible head and enemy.length >= my_length (>= because equal death), and `danger_head_win = bytearray(cells)` where enemy.length < my_length. But if multiple, fatal dominates. Need also account if cell is blocked for enemy by static obstacles? We can exclude cells in occ_others_static? If enemy moves into another snake body, it may die, but if its head and another head? For risk to me, if enemy would die simultaneously but my head also there? If my head there and enemy head there, head-on; if enemy length shorter, I survive even if enemy also dies. If enemy length longer/equal, I die. Whether enemy move is legal doesn't matter? Strong opponent won't suicide unless kills me. If equal, both die; maybe bad. Use possible regardless of other obstacles? But if cell occupied by another body, enemy would collide and die; but if head-on with me too? The rules simultaneous: if enemy head enters same cell as my head, head-on resolved; if also body? Cell could have body? If my new head is in a body cell, I'd die static; excluded. If cell is another snake's body, enemy dies due body collision, but if my head also there? The head-on rule for multiple heads into same cell; if there is also body? The cell cannot have body if I moved there safely (except tails maybe). If enemy moves into a cell occupied by a third snake's body, it dies, but if my head there, does head-on apply? The cell has my head and body? Probably head collides with body too; ambiguous. Ignore.
Better possible heads only inside and not enemy's own body. Include even if blocked by others? Maybe too conservative. Use not enemy own body.

5. Generate candidate directions. For each dir not opposite current_dir (unless no choice). Compute new coordinate. If outside: unsafe. If new_idx in occ_others_static or own_block (depending food) -> unsafe. But if new_idx is enemy possible head fatal? Not immediate static; mark risk.

Need own_block depending if new_idx in food_set:
- If new_idx food: own_block = own_full_mask (tail stays). Else own_block = own_move_mask (body[:-1]). However if my tail is unique and new_head == tail and not food, own_move_mask excludes tail, safe. If new_head == tail and food? impossible if food on body? but if yes, own_full includes tail, unsafe; okay.
But occ_others_static may include my tail? no.

Potential issue: If I move into a cell currently occupied by an enemy head, occ_others_static includes enemy head because body[:-1] includes head. So unsafe. Good.

6. For each candidate, compute features. To save time, first collect immediate safe candidates. If none, choose from all directions using least bad (maybe reverse? If all unsafe, return current_dir or random). But if no immediate safe, maybe we are doomed; choose direction with max space ignoring collision? Actually if all immediate fatal, maybe head-on risk? Could choose move that causes enemy to die too? But ranking maybe if both die same turn and I longer? In duel, if unavoidable death, try to take enemy with us? Not important. Fallback choose direction not wall maybe.

For immediate safe candidates, compute:
- `fatal_head = danger_head_fatal[new_idx]` (bool). `win_head = danger_head_win[new_idx]`.
- Maybe if fatal_head and there are nonfatal alternatives, heavily penalize.
- `space_safe`, `space_total`, `nearest_food_dist`, `nearest_safe_food_dist`, `tail_reachable`, `enemy_dist`, `centrality`.

Need efficient BFS per candidate. We can create a blocked mask for candidate:
`blocked = bytearray(cells)` maybe copy occ_others_static then OR own_block. Copy 961 bytes *4 trivial. But BFS needs visited. Could implement `flood_info(start, blocked, danger_fatal, food_set, tail_idx, deadline)` returning space, food distances.

BFS details:
- Use `collections.deque`. For speed, preallocate arrays? Could use list as queue with head index. `visited = bytearray(cells); visited[start]=1; q=[start]; head=0`. While head<len(q): pop. Count. Limit maybe cells. For each neighbor (4) if inside and not blocked and not visited. Also maybe if danger_fatal[neighbor] and we want safe space: we can either not traverse through fatal cells? If blocked by danger, may fragment. We can compute two counts in one BFS: total_count all reachable ignoring danger; safe_count only cells not danger_fatal? But if we don't traverse through danger_fatal, safe reachable may be less. Could treat danger_fatal as blocked for safe BFS. Doing two BFS heavy. Maybe one BFS with `if danger_fatal[n]: continue` for safe? But also total. Could run one BFS that traverses all reachable but counts safe separately; however safe connectivity should not traverse danger cells, but if you traverse through danger to safe beyond, safe_count wrong. Could ignore; count cells not danger but reachable through danger may overestimate safe. Maybe okay. Or run second BFS if time. Since 4 candidates, 8 BFS maybe okay? 8*961 ~ 7688, still okay. But plus enemy BFS. 50ms maybe tight but Python can do ~100k ops? 8k cells with neighbor loops ~32k, okay.

Maybe run one BFS for total space and nearest food; and compute danger penalty separately. Simpler.

BFS should treat `blocked` as occupied. Should we treat fatal danger cells as blocked? If we block them, space more realistic but may be too conservative. Could use `blocked_for_space = blocked | danger_fatal` if there are alternatives? But if fatal danger cells are adjacent to enemy heads, blocking them might leave tiny space. Strong opponents can control those cells. But avoiding them is good. We can compute space with fatal danger blocked, but if start itself fatal, space maybe 1? We'll penalize. Let's define `space_block = blocked` plus maybe fatal danger except start? Could mark fatal danger as blocked for BFS. However enemy heads move, so danger cells change; blocking all adjacent may be overly restrictive but survival-oriented.

Maybe use a `risk_block` bytearray for cells where an enemy longer/equal can move into. For BFS space, block those cells except if they are food? Hmm.

Alternative: Use distance transform: For candidate score, space_total from normal BFS; danger_count = number of reachable cells that are fatal danger; safe_ratio. Simpler.

Food distance BFS: If we use same BFS from candidate start, record min dist to any food. But if food behind danger, still reachable. Could also record min dist to food where path doesn't pass fatal danger: if BFS blocks danger. Could compute safe BFS. Let's implement two BFS? We can combine: `flood(start, blocked, block_danger=False)` returns count, min_food. For safe, blocked2 = blocked | danger_fatal (but ensure start not blocked; if start danger, safe BFS just start? maybe count 1). Then space_safe, food_safe_dist. Use safe primarily if non-zero. Time okay.

Tail reachability: Could use BFS safe/blocked. Target tail_idx after move. If tail moves (not eat and new tail not duplicate?), target cell = new_body[-1]. But if target in blocked? Tail cell is not blocked if tail moves. We can check reachable in BFS ignoring danger? For classic, tail reachable if BFS from start to tail on blocked where tail allowed. Our blocked excludes own tail if not grow. For candidate not eating, own_move_mask excludes old tail, but new tail is old body[-2]? Let's simulate: old body [h,n,...,t2,t]. Not eat: new_body=[new,h,n,...,t2]. New tail = t2. In blocked for after move, we used own_move_mask=old body[:-1] = [h,n,...,t2] includes new tail t2. That means BFS would treat new tail as blocked, so cannot reach it. For tail reachability, we need allow target tail cell even though currently occupied by tail segment that will move next turn? Wait after this candidate move, new tail t2 is occupied. Next turn, if not eating, tail t2 will move, so cell t2 becomes empty. In classic check, you allow moving into current tail because it will vacate. For BFS after move to see if head can reach tail, you should treat tail cell as passable/target. So blocked should exclude new tail if it will move next turn. Our own_move_mask includes new tail because it's part of body after move except tail? Need compute own_block_for_space = new_body[:-1] if tail will move next turn, i.e., exclude new tail. But for immediate collision, own_block should include all old body except old tail? Let's clarify.

Immediate candidate safety: When moving now, new head cannot collide with existing body segments that remain. Existing body after tail moves: old body[:-1] (includes old head, neck,..., t2). It includes new tail t2 because after move t2 will be tail and occupies that cell. But new head cannot move into t2 unless t2 is old tail? If old length >? Moving into t2 (second-to-last) is collision because that segment remains. So immediate blocked includes old body[:-1]. Good.

For future space after the move, the snake's new body is [new_head, old_head,...,t2]. The tail t2 will move next turn if not just ate. Thus for reachable space from new head (for next decisions), t2 should be considered passable (will vacate) if we are computing one turn later. But the body still occupies t2 at the end of this turn; however when considering path starting next turn, first move can go into t2 if tail moves. So space BFS should block new_body[:-1] (exclude new tail) if tail will move next turn. For candidate if not eating this turn, after move tail will move next turn unless we eat next turn; approximate exclude new tail. If eating this turn, new tail = old tail and tail will not move next turn, so block all new_body (exclude none). Thus for BFS space, blocked_self_after = new_body[:-1] if not eating else new_body. But new_body includes new_head; start is new_head, should not block start. So block old_head... up to second-to-last. For not eating: block old_body[:-1]? That includes t2 (new tail). Wait new_body = [new] + old_body[:-1]. new_body[:-1] = [new] + old_body[:-2]? Excluding new tail t2. But start new should not block. So block old_body[:-2] (old head through third-last). This excludes old tail t and second-last t2. Is old tail t empty after move? yes. t2 is new tail but will move next turn, so passable. This is more open. But is it safe to treat t2 passable? If we move next turn into t2, tail moves simultaneously, yes if not eating. Good. For immediate safety, we didn't allow moving into t2 (unless it was old tail? Actually old tail t allowed, t2 not). For future space, allow t2. This is classic.

If eating this turn: new_body=[new]+old_body. Tail old tail t remains (doesn't move next turn), so for future space block new_body[:-1]? Tail should be blocked. new_body[:-1] includes new head? exclude start, block old_body all. So block old_body all. Good.

Thus need separate masks:
- `own_block_immediate`: old_body if eating else old_body[:-1]. But if eating, new head cannot be in old_body anyway; use old_body all. If not, exclude old tail (old_body[-1]) but duplicates? If old_body[-1]==old_body[-2], excluding only last duplicate still leaves cell blocked by previous duplicate in old_body[:-1]. Good.
- `own_block_space`: if eating: old_body all (excluding start if present? start new not in old_body); if not eating: old_body[:-2] (exclude old tail and new tail old_body[-2]). Need if length small (initial length 3): old_body[:-2] excludes two cells, maybe only head? Example body [s,s,s], not eat: old_body[:-2]=[s]. Blocks spawn? But after move new_body [new,s,s], new tail s, will move next turn? Actually there are two s segments; next turn tail moves one s, leaving one s. So spawn cell s remains occupied even if tail moves because duplicate. Excluding old_body[-2] still leaves old_body[-3]? For length 3, old_body[:-2] = [s] (head). But old head s will be occupied by neck? Wait old body all s. After move: [new,s,s]. Future next turn if not eat: tail moves, body [new2,new,s]. The cell s remains occupied by tail after next move? At the moment after candidate, there are two s. The new tail is s (last). If tail moves next turn, one s removed, but another s remains as body[-2]? Actually new_body [new,s,s]; new_body[:-1] = [new,s] blocks s. For space from new head for next turn, cells occupied that will remain after next move? We need block new_body[:-1] excluding new tail? Classic assumes no duplicates; with duplicates, if tail cell duplicate, it remains occupied even if tail moves. So simply excluding new tail when duplicate is wrong. Need multiset logic. For future space, a tail cell is passable only if the number of segments in that cell that will leave? General: after candidate, new_body. For next move, occupied cells that remain (excluding new head movement) = new_body[:-1] if tail moves, but if new_body[-1]==new_body[-2], tail cell remains in new_body[:-1]. So to get cells blocked for path next turn, use new_body[:-1] if tail will move, new_body if tail stays. This includes duplicate tail. Then exclude start? new_head is in new_body[0]; new_body[:-1] includes new_head, but start should be passable? For BFS from new head, we should not block start. We can create blocked = other obstacles + (new_body[1:-1] if tail moves else new_body[1:]). That excludes start; includes neck...; excludes tail only if tail moves and tail cell not duplicated in new_body[1:-1]? If duplicate, tail cell equals body[-2], which is included in new_body[1:-1] because body[-2] not excluded. Good. So formula: for after move future space, block own segments except head, and also exclude tail if it will move? Actually new_body[1:-1] excludes tail. If tail duplicate, body[-2] same cell as tail and is included (unless length 2?); so cell blocked. Perfect. If tail stays, block new_body[1:] (includes tail). Good.

Thus we can compute own_space_block after candidate from simulated new_body:
- new_body = [new_idx] + (old_body if eating else old_body[:-1]) (but if old_body length? yes)
- tail_stays_next = eating or (len(new_body)>=2 and new_body[-1]==new_body[-2])? Actually if not eating but duplicate tail remains due initial, tail cell still occupied, but tail segment moves? For path, we need block as above. We can just decide exclude tail from block only if not eating and new_body[-1] != new_body[-2]? Wait if new_body[-1]==new_body[-2], new_body[1:-1] includes body[-2] same cell, so tail cell blocked. If unique, not. So use block_own = new_body[1:] if eating or duplicate_tail? else new_body[1:-1]. But new_body[1:-1] already handles duplicate? If duplicate, body[-2] included, so tail cell blocked, but the tail index itself excluded; same cell still blocked. So simply `own_block_space = new_body[1:] if eating else new_body[1:-1]`. This works because duplicate remains via body[-2]. But if length=1? not. If new_body length 2 and not eating, new_body[1:-1]=[] excludes tail, okay. If duplicate length2 [a,a]? eating? okay.
- But note if not eating and old_body had duplicate tail, new_body may have duplicate tail? Example old [h,t,t], not eat -> [new,h,t,t]? Wait pop last -> [new,h,t] if old length3? Actually old body [h, t, t] (two tail same). old[:-1]=[h,t]. new_body=[new,h,t]. No duplicate tail unless h==t. Initial old [s,s,s] -> old[:-1]=[s,s]; new_body=[new,s,s], duplicate tail. new_body[1:-1]=[s], blocks tail cell. Good.

For immediate own_block: if eating: old_body (all) else old_body[:-1]. This also handles duplicates.

For other snakes' static occupancy (for immediate and space), we can use their current body after their next move? We don't know their new heads. For static obstacles, use current body after tail move: if their tail_stays (last two overlap) then body all else body[:-1]. This is equivalent to cells occupied after they move, excluding new heads. For future space, should we exclude their tails if moving? body[:-1] already excludes unique tail; duplicate tail remains. Good. We don't know their new heads, but current head remains occupied by neck, so included. Good.

For space BFS, blocked = occ_others_static OR own_block_space. This treats other tails moving this turn, but next turn they move again; approximate. Could be optimistic.

For immediate safety, blocked = occ_others_static OR own_block_immediate. But occ_others_static includes other current heads (occupied by neck). Good.

Now tail reachability: We can check if own tail cell (new_body[-1]) is reachable in BFS using blocked_space but tail cell may be blocked if duplicate? If tail unique, blocked_space excludes it, so reachable possible. If duplicate, tail cell blocked, so tail_reachable false. That's okay; duplicate means tail not effectively chasable. But if eating, tail stays blocked false.

Food distance BFS: Use blocked_space? For path from new head to food in future, own tail passable, other tails passable. Good. But food might be on a cell currently occupied by moving tail? Food shouldn't. Use blocked_space. If food cell blocked (by body), unreachable; maybe food appears in empty only.

Head danger mask for space: Could incorporate enemy possible heads based on current positions. But after our move, enemies also move; danger for future changes. Maybe ignore in BFS, just penalize candidate new head and maybe food path passes near enemies. Could compute `enemy_dist_map` from enemy heads using obstacles occ_others? Then candidate penalty = -min enemy distance. But BFS distance not Manhattan. Could compute one multi-source BFS from enemy heads on grid blocked by occ_others_static? But enemy heads themselves start; obstacles? For threat, simpler Manhattan distance to enemy heads. For 31x31, okay. Candidate with min Manhattan <=1 fatal risk, <=2 caution.

Maybe compute `enemy_proximity = min(manhattan(new_head, enemy.head))`. Prefer larger. But if chasing food near enemy, tradeoff.

Food selection with enemy distances: Could compute BFS from enemy possible heads? Maybe overkill.

Let's propose scoring formula:
For candidate c:
```
if immediate_unsafe: score=-1e9
else:
  fatal = danger_fatal[new_idx]
  # If fatal and any nonfatal safe candidate, deprioritize
  base = 0
  if fatal: base -= 100000
  if win_head: base += 500? (maybe aggressive)
  space_weight = 8
  food_weight = 12 if health<60 else 5
  risk_weight = 2000? Need calibrate.
  score = base + space_safe*space_weight + space_total*1 - food_dist*food_weight - enemy_close_penalty + centrality
```
But absolute scales: space up to 961, food_dist up to 100. If space weight 5, food weight 20. Need prioritize survival: fatal penalty huge. Then space vs food. We want not starve: if health low, food weight high. Maybe use tuple instead of weighted to avoid tuning.

Tuple approach:
```
key = (not fatal, tail_reachable, space_bucket, -food_dist, -enemy_close, centrality)
```
But space_bucket could dominate food: always choose max space even if far food, may starve. Need balance. Could use health-dependent: if health < 30, prioritize food_dist among tail_reachable. Otherwise space.

Maybe rank:
1. immediate safe.
2. if any candidate without fatal head risk, restrict to those. (Unless health very low? Still maybe.)
3. if any candidate with tail_reachable and space >= threshold? Hmm.

Classic snake: prioritize moves that keep tail reachable. If multiple, choose closer food. If none tail reachable, choose max space. This is strong. For multiple opponents, tail reachable not enough but good.

Let's implement:
- Compute features for safe candidates.
- Partition candidates:
  A: not fatal_head and tail_reachable and (space_safe >= my_length maybe)
  B: not fatal_head and tail_reachable
  C: not fatal_head
  D: all
Choose first non-empty group. Within group, score by food distance (safe food), space, enemy proximity.
But if health low, maybe need ignore tail_reachable to get food? If no tail_reachable path to food, may need. Health 100; if low, maybe choose food even if tail false. Could if health < 30 and candidate food_dist small, include.

Tail reachable definition may be too strict with opponents. It may cause bot to circle tail and ignore food, starving if tail reachable but no food. Need within tail_reachable choose food_dist; if all food unreachable? Then wander. If health decreases, eventually may need unsafe. Could add urgency: if health < 40, group by not fatal and food_dist reachable, not necessarily tail. Or score tail_reachable as bonus not hard.

Maybe scoring weighted with large tail bonus but not hard. Need robust.

Let's think of typical states. On empty board, tail reachable for moves that don't trap. Food distance guides. If a move goes into narrow corridor to food but tail reachable? maybe. If tail not reachable, avoid. Good.

For multi-snake, tail reachable may be false due other bodies blocking; still need move. Use space.

Could implement scoring as:
```
score = 0
if fatal: score -= 1_000_000
if tail_reachable: score += 100_000
if space_safe < length*2: score -= 50_000? (trap)
score += space_safe * 5 + space_total * 1
score -= food_dist * (200 if health<50 else 50)
score -= enemy_proximity_penalty
score += centrality
```
This allows food urgency to override tail if very close? 100k tail bonus huge; food_dist max 100*200=20k, so tail dominates. Maybe okay; survival first. If tail_reachable but no food reachable for long, health declines; when health critical, could reduce tail bonus? We can make tail bonus = 100000 if health>30 else 20000. Or health weight.

Maybe use `survival_score` = tail_reachable*100000 + space_safe*100 - fatal*1e6. Food weight = 1000 if health<30 else 200. Max food_dist 100 -> 100k, can override tail if health critical. Tune.

But need not overfit. Simpler: Use lexicographic but with health threshold.

Potential stronger: Use path to food with safety check. Instead of one-step tail reachable, simulate full path to food and check tail reachability after eating. This chooses food only if safe. Could implement for each food path. But one-step tail reachable maybe enough.

Let's consider implementing `choose_move_by_target` with full path safety:
- BFS from my head to each food on blocked grid (others static + own body except tail?); get path.
- For each food path, simulate my snake along entire path, eating at end, assuming other snakes static? Then check if after eating, tail reachable / space. If safe, choose first step.
This can avoid paths that trap after eating. But other snakes move. For single snake classic strong. For multiple, maybe. Time: paths length up to 100, simulate BFS per food (3 or 12). Could be okay. But need choose among candidate moves maybe easier.

Full path algorithm:
1. Build grid blocked by other snakes' occupied_next and my body except tail? For pathfinding, my tail cells can be traversed as they move. But path length >1, tail moves along; complex. Simpler use static obstacles.
2. Find shortest path to each food. Score by my_dist vs enemy_dist. Choose best safe path: simulate my body moving step by step along path (pop tail unless food at end). At each step, check collision with static obstacles? Not. After reaching food and growing, check tail reachable/space. If safe, return first move. If none safe, fallback heuristic.
This might be too optimistic and could move into head-on. Need immediate risk check for first step.

Maybe combine: candidate heuristic already ensures immediate safe. Full path not necessary.

Need handle head-on with longer enemy. We can derive enemy current direction to exclude reverse. But in state we don't know their last direction if body collapsed. Use body if head != neck. If collapsed, possible all dirs.

Derive directions:
```
DIRS = {'up':(0,-1), ...}
OPP = {'up':'down',...}
```
Coordinates: x,y. idx = y*w+x. Need neighbor calculations. For speed, precompute neighbors for current board size? Since board size can vary per game but same within game. Use global cache `neighbors_cache` keyed (w,h) maybe. But each game new process, one board size. We can build arrays: `neighbors = [[] for _ in range(cells)]`, `dir_to_idx = {}`? For each cell and direction, next idx or -1. This speeds BFS. Build once in global. Since decide first call, use state dimensions. Need not heavy: cells <=961, 4 neighbors. Use global variables.

Global cache:
```
_grid_info = None
def get_grid(w,h):
  global neighbors, dir_delta, ...
```
But if width/height same across? okay.

Precompute for each cell four next indices for directions in order up/down/left/right. Also x,y coords maybe for Manhattan/center. `coords = [(x,y)]`.

Directions order maybe ['up','down','left','right'].

Current direction derivation using idx: If head != neck, delta = head - neck. But idx difference depends on width. If head == neck +1 => right; -1 left; +w down; -w up. Need ensure not wrapping; body adjacent. Use coords maybe easier. Body stored as idx; we can compute dx,dy from coords. But converting each time okay. Precompute `xy[idx]`.

For each snake, body_idx = [y*w+x for x,y in body]. Need do every turn. For 11 snakes length maybe up to? Could be long (hundreds). Conversion O(total length). Total cells 961, okay.

Occupancy masks building:
Use bytearray cells. For each enemy:
```
body = ...
tail_stays = len(body)>=2 and body[-1]==body[-2]
mark = body if tail_stays else body[:-1]
for p in mark: occ[p]=1
```
But if multiple snakes, okay. For own masks: old_body = my_body. own_immediate_not_eat = old_body[:-1]; own_immediate_eat = old_body. Could make bytearrays? For candidate, checking `if occ_others[p] or (p in own_block)`. Since own_block small list, could use bytearray for own too. Build `own_full_mask`, `own_move_mask` (old_body[:-1]). For immediate: if p in food_set use own_full_mask else own_move_mask. But if p is food and own_full_mask[p] true, unsafe. Food shouldn't be on body. Good.

For own_space_block per candidate, need simulate new_body and mark. Could avoid creating list each candidate by determining which old segments to block:
- If eating: block old_body all (except start not in old). So own_space_mask = own_full_mask.
- If not eating: block new_body[1:-1] = old_body[:-2] plus? Wait new_body=[new]+old_body[:-1]; new_body[1:-1] = old_body[:-2]? Let's test: old len L. old[:-1] len L-1. new len L. new[1:-1] indices 1 to L-2 -> old[0:L-2] = old_body[:-2]. Yes. If duplicate tail, old_body[:-2] may still include duplicate cell? Example old [s,s,s], old[:-2]=[s], blocks s. Good. If old len 3 [h,n,t], old[:-2]=[h], blocks old head; new body [new,h,n], new tail n, but old_body[:-2]=[h], does not block n (new tail) which is passable next turn. Correct. But what about old neck n? It becomes tail and will move next turn, so passable. Good. However immediate own_move_mask old_body[:-1] = [h,n] blocked n for current move; can't move into neck. Future space allows n. Good.
Thus own_space_mask if not eating = mask of old_body[:-2]. If length <2? old len 3 minimum. If old len 2? not. If old len 3, old[:-2] length1.
If eating: own_space_mask = old_body all (tail stays). But after eating, new_body=[new]+old; new_body[1:] = old, yes.
But if eating and old tail duplicate? okay.
For candidate if new_head is food, own_space_mask=own_full_mask; else own_space_mask=own_short_mask (old_body[:-2]). Need ensure start new_head not in these masks; if it is, immediate unsafe anyway. For BFS, if blocked[start] true due own mask? Should not if safe; but could if new_head in old_body[:-2]? immediate unsafe. So okay.

But wait for future space after not eating, should we block other snakes' tails that moved this turn? occ_others_static = body if tail_stays else body[:-1]. But next turn their tails may move again; current occ maybe too conservative. However okay.

For BFS blocked = occ_others_static | own_space_mask. But occ_others_static includes enemy current heads (occupied by necks after this turn). At future turn, those heads have moved, but we don't know where. Conservative.

Tail target after candidate: If not eating, new_tail = old_body[-2] if len>=2 else old_body[-1]? If eating, new_tail = old_body[-1]. For tail reachability, target should be new_tail and should be passable if not duplicate? In blocked mask, if not eating, own_space_mask=old_body[:-2], so old_body[-2] not blocked unless duplicate with earlier. Good. If eating, tail blocked, tail_reachable false (unless start==tail impossible). If not eating but old_body[-2]==old_body[-3] duplicate, own_space_mask includes old_body[-3] same cell, so target blocked -> false. Good. We can check BFS visited target.

But if old length 3 initial [s,s,s], not eating: new_tail=old_body[-2]=s, own_space_mask=old_body[:-2]=[s], target blocked -> tail_reachable false. That's okay early; space maybe enough. But classic tail chase not available while stacked.

Food BFS: Need food_set indices. For candidate, BFS from new_idx on blocked_space. Record min distance to any food. But if food cell blocked? If blocked_space[food] true, not reachable. Could happen if food on own body? no. If food on other body? food spawns empty, but bodies move; maybe state food could be under a snake? Probably not. If blocked, ignore.

Safe BFS with danger: Let's create `danger_fatal_mask` for enemy possible heads where enemy length >= my_length. But enemy length may change if they eat this turn? Unknown. Use current. For candidate new head, if danger_fatal true, high penalty. For BFS safe space, we could block danger_fatal cells (except start) to avoid areas enemy can contest. But if enemy possible heads are many, might block too much. Maybe create `threat_mask` = danger_fatal. For safe BFS, blocked_safe = blocked | threat_mask, but if start in threat, allow start? If start threat, safe_space = 1 maybe. This may be too conservative but survival. Could compute both total and safe. Use safe in score primarily. But if safe_space too small due adjacent enemy, we may choose another move. Good.

Build enemy possible heads more accurately:
For each enemy:
- Determine its current_dir if possible from body head/neck; else None.
- For each dir not opposite current_dir (if known): next cell inside.
- Check if next cell is not in enemy's own immediate block? Enemy's own immediate block: if enemy tail_stays? body all else body[:-1]. But if next cell is its tail unique, allowed. If next cell in other occupancy? Could still be head-on/body; but for risk maybe exclude if in occ_others_static? occ_others_static includes other bodies and my old body? It includes my old body except tail. If enemy moves into my old body, it might die, unless my tail moves. But if my new head is there? Not. To be conservative include all inside not own body. But if we include cells occupied by my old body, enemy could move into my old head (which will be occupied by my neck) and die; not a threat to my new head unless my new head there (not). For risk to my new head, new_head is not my old body if safe. So excluding other bodies okay. Use not enemy own block only. If enemy current_dir unknown, all dirs.
- Mark if enemy.length >= my_length: fatal else win. If multiple, fatal if any. But what if enemy length equal but we have just eaten? length current. okay.

Need also consider enemies could grow this turn by eating food, making longer. If they can move into food and my new head same? Head-on at food: if both eat, length both grow? Rule: two heads same food both eat. If enemy length = my_length-1 and eats same food, after grow length equal? Collision resolution uses length at elimination step after eating? Order: eat food step 3, elimination step 4. If two heads same food, both grow, then head collision resolved by length after growth? It says longest survives. If both eat same food, both grow, lengths increase. So if enemy length < my_length by 1, and same food, after eating both +1, still enemy shorter by 1. If enemy length equal, both +1 equal. So current comparison okay. If enemy could eat different food and then head-on? They can't eat and move into my head unless my head on food? If new_head is food and enemy moves there too, both eat. Comparison current lengths okay. If enemy eats another food? no.

But if I move into food and grow, my length for head-on should be current length +1? Step eat before elimination. If my new_head food and enemy head also moves there, both eat, both +1, relative same. If enemy moves into my new_head which is not food, lengths unchanged. If I eat food but enemy moves into my new_head? Can't, same cell food, both eat. So current length comparison okay. If only I eat and no head-on, not relevant.

What about my length used for fatal risk should be effective length after eating if new_head food? If enemy not sharing food? No head-on. If enemy moves into my new_head (food), both eat, relative same. So current okay.

Could include possible head risk for cells that are food: if enemy possible and length >= mine, fatal. But if food makes both grow, equal remains fatal. okay.

Need maybe avoid moving into cell adjacent to enemy head if enemy is longer, but if that cell is the only path to food and enemy likely not choose? Hard.

Now, candidate feature computation function:
```
def evaluate_candidate(dir_idx, new_idx, eating, blocked_immediate, own_space_mask, tail_target):
    blocked_total = OR occ_others, own_space_mask
    # BFS total maybe with threat blocked? We'll implement flood(blocked, threat_block)
```
Need OR bytearrays efficiently. For each candidate, copying `blocked = occ_others_static.copy()` then OR own mask. Own mask could be bytearray. Build own_space_mask_eat and own_space_mask_no_eat bytearrays once. For immediate, own_full_mask and own_move_mask.
- `own_full_mask`: mark old_body all.
- `own_move_mask`: mark old_body[:-1].
- `own_space_eat_mask`: same full.
- `own_space_no_eat_mask`: mark old_body[:-2].
But for initial duplicates, old_body[:-2] may mark spawn; okay.

For BFS, need blocked as bytearray. Copy occ_others (len cells) per candidate. 4*961 copy trivial. Then for i,val in enumerate(own_mask): if val: blocked[i]=1. But iterating full cells maybe okay. Could optimize by marking list cells: own_space_lists. For immediate check, just use mask.

Better: Build masks as bytearray, and in BFS treat two masks separately: `if occ_others[n] or own_mask[n]: blocked`. Avoid copying. BFS neighbor check can check occ_others or own_mask. But for safe BFS also threat. Function call overhead. Could pass masks.

Implement BFS:
```
def flood(start, occ_others, own_mask, threat_mask, food_arr, deadline):
    if occ_others[start] or own_mask[start]: return ... # shouldn't
    visited = bytearray(cells)
    visited[start]=1
    q=[start]; qi=0
    total=0; safe=0; min_food=INF; min_safe_food=INF
    while qi < len(q):
       p=q[qi]; qi+=1; total+=1
       is_safe = not threat_mask[p]
       if is_safe: safe+=1
       if food_arr[p]:
           dist = ??? need distance. Need store distances.
```
Need distance to food. Could store dist array or queue of (p,d). To avoid tuple overhead, use parallel dist list or array. Since cells <=961, can use `dist = [-1]*cells`? Alloc per BFS heavy but okay. Or use `dist = bytearray(cells)` with 255 max? Board path <= 961 >255. Use `array('H')`? Simpler: queue list of ints and separate `dist` list of int initialized -1 each BFS. 4*961 ints okay. But time. Could use dictionary? no.
Maybe BFS level by level: `current_level list`, distance increment. For food min distance, we can stop at first food if BFS level order. But need count space too; could continue. Use queue with distances stored in parallel list: `dists = [0]*cells`? Alloc. Or use `dist = {start:0}` slow.
Could use `visited` bytearray and `dist_arr` global int array reused with timestamps? More complex. Given small board, simple `dist = [-1]*cells` per BFS acceptable? 4 BFS * 961 ~ 3844 list allocations; okay per turn? 50ms maybe list allocation cost moderate. Could optimize with `array('h', [-1])*cells`? Not needed.
Maybe level BFS:
```
q=[start]; visited[start]=1; dist=0; min_food=INF
while q:
  next=[]
  for p in q:
    if food[p]: min_food=min(min_food, dist)
    for n in neighbors[p]: if not visited and not blocked: visited[n]=1; next.append(n)
  q=next; dist+=1
```
This counts and finds min food. It doesn't need store distances. But list allocations per level. Max dist 62, okay. For 4 BFS, fine. Could also break for food? Need space count; continue. If only need min_food, could stop expanding after min_food found? But need space. Could cap space count at maybe 500 for speed. But full okay.

For safe BFS with threat blocked, we can run separate flood with `blocked_threat = True` if threat_mask[p] and p!=start? We can implement `flood(start, occ, own_mask, block_threat=False, threat_mask=None)`. In neighbor check, if block_threat and threat_mask[n] and n != start: skip. Count safe cells. For total, block_threat False. For min_food safe, use block_threat True. But two BFS per candidate doubles. Maybe run only safe BFS (threat blocked) and if start threat, allow start but don't expand through threat? If start threat, safe BFS will have start, neighbors threat blocked? Could be zero. Use safe_space as primary. Total space maybe not needed. Could run one BFS with threat blocked. This yields conservative space/food. If too conservative, maybe still okay. To avoid missing path through threat when no alternative, we can if safe candidates none use total. But we can compute total only if needed. Simpler: compute `space, food_dist` with blocked including threat_fatal. Also compute tail_reachable in same BFS (target reached). If start threat, we still count start but may not expand; candidate penalized by fatal flag.

Will blocking threat_fatal cause bot to think no space when adjacent to longer enemy, maybe choose wall? But if all moves adjacent, it will still choose among low safe_space. Maybe okay. Could also not block threat for BFS but penalize. Let's decide.

Maybe better: BFS blocked = occ_others + own_space. Do not block threat. Compute space_total and food_dist. Add fatal penalty. This avoids over-fragmentation. But then space may include cells enemy can enter. We can subtract threat_count? Could count threat cells visited. We can in BFS count `danger_cells` where threat_mask[p]. Score penalty. Simpler. Let's do one BFS no threat block, count total, count safe_cells (not threat), min food, tail_reachable. Use safe_space = count of cells not threat. If fatal start, safe_space maybe less. This gives info.

BFS level implementation with food set as bytearray `food_mask`.
```
def flood(start, occ, own_mask, threat_mask, food_mask, target_tail):
 visited=bytearray(cells); q=[start]; visited[start]=1; dist=0; total=0; safe=0; min_food=INF; tail_reach = (start==target_tail)
 while q and time<deadline:
   next=[]
   for p in q:
     total+=1
     if not threat_mask[p]: safe+=1
     if food_mask[p] and min_food==INF: min_food=dist # BFS level first food
     if p==target_tail: tail_reach=True
     for n in neigh[p]:
       if not visited[n] and not occ[n] and not own_mask[n]:
          visited[n]=1; next.append(n)
   q=next; dist+=1
```
Need deadline check maybe per level. If time out, return partial? Could cap. But BFS small. For safety, if process_time > deadline, stop and use current counts.

But `threat_mask` for safe count: threat_fatal only. Maybe also include enemy possible win? not fatal. Safe count excludes fatal. Good.

Tail reachability: Need target_tail passable. If target_tail blocked by own_mask/occ, BFS won't reach. If target_tail is start? possible? no. If target_tail threat, still tail_reach true if reached; but dangerous. okay.

Food distance: If no food reachable, INF. BFS first food distance. If multiple food, okay.

Need candidate score. Let's define my_length = my_snake['length'] or len(body). health = my_snake['health'].
Food urgency: `hunger = 100 - health`? Actually health decreases; low health urgent. Use `health`.
Weights maybe:
```
fatal = threat_fatal[new_idx]
win = threat_win[new_idx]
space = safe_space if safe_space>0 else total_space
food = min_food if <INF else 9999
tail_bonus = 1 if tail_reachable else 0
# If health > 60: prioritize tail/space; if health < 40: food.
score = 0
if fatal: score -= 1_000_000
if tail_reachable: score += 200_000 if health>30 else 50_000
if space < my_length*2: score -= 100_000  # avoid trap
score += space * 20
# food reward: if reachable, subtract distance * weight
food_weight = 5000 if health < 30 else 1500 if health < 60 else 500
score -= food * food_weight
# If no food reachable, maybe prefer space.
# enemy proximity: min Manhattan distance to enemy heads
score += min_enemy_dist * 30 (max maybe 30*30=900) small
# centrality: distance to center, prefer center small: score -= center_dist*5
# win head: maybe +2000 if longer (aggressive) but not too.
if win: score += 5000? Could encourage killing but risk. Maybe small.
```
But tail_bonus 200k vs space 20*961=19k, food 100*5000=500k if health low. So low health food can override tail. If health high, tail dominates. Trap penalty 100k can override tail if space tiny. Need calibrate.

Maybe fatal penalty 5 million. If all fatal, choose best.

Could use tuple for immediate groups and score within. Weighted may be unpredictable. But okay.

Need ensure not too slow due scoring. Could simplify weights.

Alternative scoring with normalized features:
```
key = (not fatal, tail_reachable, -food if health critical else space)
```
Hmm.

Let's test mentally. Start turn 1, no threat, tail_reachable false due stacked. Food distance maybe. Score chooses move toward food/center. Good.

If two moves: one tail_reachable space 20 food dist 10, other tail false space 30 food dist 1. Health high: tail bonus 200k wins. Good. Health low (<30): tail bonus 50k, food weight 5000*9=45k, space difference 200, maybe tail still wins if food diff <10. If starving, might choose food if much closer. Good.

If space < length*2, trap penalty 100k, may avoid even tail reachable. If length large, threshold maybe high. But if only move, choose.

Maybe `space` should be safe_space excluding fatal threat. If safe_space small due threat, penalty. Good.

Need consider head-on risk fatal: If candidate new_head is possible enemy head and enemy length >= mine. In many cases when enemy adjacent, moving away may still be possible enemy head? Example enemy head at (5,5), I head at (5,6) below. My possible move down to (5,7). Enemy possible heads include (5,6) (my current), (4,5),(6,5),(5,4), not (5,7). So no fatal. Moving sideways maybe not. If I move toward enemy's adjacent cell, fatal. Good.

But enemy could move in same direction and stay ahead, not immediate head-on. Threat not captured. Fine.

Need avoid walls: BFS space will be low near walls. centrality small.

Now, can we improve with "enemy body avoidance" by considering possible enemy next heads as obstacles? We treat as threat not blocked. Maybe if enemy longer possible head, we should hard exclude if alternative. Fatal penalty 1e6 does that. If all moves fatal, choose best. Good.

Need handle simultaneous food: If multiple food and enemies, okay.

Potential issue: Our own current direction and reverse. If we return opposite, judge ignores and continues original. This could cause our planned move not happen, and global last_dir wrong. We should avoid returning opposite if current_dir known. But if all non-reverse immediate unsafe, maybe returning reverse (actual old dir) might be safer? Since reverse invalid means actual direction continues; we can evaluate original direction as candidate? The current_dir itself is always non-reverse. If current direction leads into wall, but all turns unsafe? Maybe cannot avoid. We should include current_dir candidate. If we choose opposite direction, actual move is current_dir, not evaluated. So never return opposite unless we intend actual current_dir? Better: filter out opposite from candidates; if no candidates, return current_dir if known else 'up'. But if current_dir immediate unsafe and other directions also unsafe, maybe choose some direction? If reverse invalid, returning reverse results current_dir (same as unsafe). Could choose any; maybe random. But to keep model, don't return opposite. If current_dir unknown (collapsed), no opposite.

Derive current_dir: If body head != neck. But initial stacked, unknown. Use last_dir. At turn 1 last_dir None. After first move, state turn 2 body may still stacked? Example start [s,s,s], move up -> [new,s,s], head != neck, derive. Good. Set last_dir to returned direction. If returned direction not actual due invalid? we avoid.

Need update global last_dir after decide. But if decide_main returns, set last_dir. If fallback, set maybe. Also store last_head? Could detect if state turn reset (turn==1) reset globals? Since new process per game, not needed. But if module reused across games? It says new independent process each game, globals clear. But safe: if turn==1, reset last_dir=None.

Need handle `state['you']` id may not be in snakes if died? But decide only called while alive? Probably. If not, return 'up'.

Now, consider rules about dead snakes disappear. Our occupancy only alive. Good.

Food count: state food list. Convert to set/mask.

Time management: Need avoid long BFS. Could have global deadline. In decide_main, if turn==1 deadline = start+0.8 else start+0.04. Check before expensive. If time left < 5ms, use quick_score maybe immediate safety only. Simpler: BFS small. But need not exceed. Implement `time_left()` and if <0.005, break candidate evaluation and choose best so far. For first turn more.

But Python `time.process_time()` CPU time. Use `time.perf_counter`? Limit CPU, but perf correlates. Use `time.process_time` for accuracy. However process_time may not include? Use it.

Potential CPU burst on load: Precomputing neighbors first turn within 1s. okay.

Now, possible stronger: Use "opponent head collision if same cell as possible head and my length > enemy" maybe not fatal, but if we are longer, moving there could kill enemy. Could be beneficial if enemy is chasing us? But if they choose not, no effect. Win head bonus small. But if enemy is longer/equal, avoid.

Need maybe consider if enemy possible head cell is occupied by food and both eat; if equal, both die? Actually if equal length and heads same cell, both die (same length). If we are shorter, die. If longer, survive. Good.

Now, let's think about endgame. If max_turns approaching, ranking: if alive at turn limit, compare length. Need eat to grow if possible. But survival still. If turn > max_turns-20, maybe prioritize length (food) more. Add `endgame = max_turns - turn < 30`; increase food weight. But if risk fatal, avoid? At end, if tied alive, length matters. Could take calculated risks if not fatal. Increase food weight. Also if only me and one enemy alive and both likely alive to limit, need outlength. In duel, if we are longer, can play safe; if shorter, need food. Could adjust based on relative length. For num_snakes==2, compare enemy length. If I longer, avoid head risk and maintain; if shorter, increase food weight and maybe win_head aggression. For brawl, many. Add features:
- `my_length`, `max_enemy_length`, `i_am_longest = my_length >= max_enemy_length`. If not longest, head fatal risk more important. If longest, maybe can use head-on to kill? But avoid equal risk.
- If endgame and I am not longest, food weight high.

Could implement dynamic weights:
```
health_factor = 1 if health>60 else (2 if health>30 else 4)
end_factor = 1 if turns_left>50 else 2 if >20 else 4
relative_factor = 1 if i_am_longest else 1.5
food_weight = 300 * health_factor * end_factor * relative_factor
tail_bonus = 200000 if health>40 and not endgame_critical else 50000
space_weight = 30
```
Need not too complex.

Maybe use score tuple with integer weights:
```
fatal_penalty = 10_000_000
tail_bonus = 1_000_000 if health > 35 else 200_000
trap_penalty = 500_000 if space < max(10, my_length) else 0
space_score = safe_space*50 + total_space*5
food_score = -food_dist * food_weight (food_weight 2000...20000)
enemy_dist_score = min_enemy_dist*100
centrality = -center_dist*10
win_bonus = 20000 if win and i_am_longest? maybe
```
If food_dist max 100, food_weight 20000 -> 2,000,000 can override tail_bonus if critical. okay.

Need ensure if no food reachable, food_dist = 1000, penalty huge; but maybe all unreachable due obstacles; then choose space. Use if food_dist >= INF/2: food_score = -10000 (not huge). Let `food_pen = food_dist * food_weight if food_dist < 900 else 50000`. But if no food reachable, we still need move; shouldn't penalize all equally. Set `food_dist_eff = min(food_dist, 200)` so max penalty bounded. If no reachable, 200. That way unreachable food not huge difference. If health critical and no reachable, space.

Maybe `food_dist_eff = food_dist if food_dist < 9999 else 999`. Weight up to 5000 -> 5M maybe. Keep moderate.

Let's decide weights after more thought.

Alternative approach: Multi-objective lexicographic with score components:
- If health > 50 and turns_left > 30: prioritize (not fatal, tail_reachable, safe_space desc, food_dist asc).
- If health <=50 or endgame: prioritize (not fatal, food_dist asc if reachable, safe_space desc, tail_reachable).
Could be simpler and less weight tuning. Implement by sorting with key depending on mode.
For normal:
```
key = (not fatal, tail_reachable, safe_space > length*3, -safe_space, -food_dist if food_dist<INF else 0, min_enemy_dist)
```
But food_dist negative: smaller distance better, so use -food_dist (larger for small? If food_dist 5 -> -5, 10 -> -10, max chooses -5). Good.
For hungry:
```
key = (not fatal, food_dist < INF, -food_dist, tail_reachable, safe_space)
```
This may be robust. But safe_space scale vs food? Lexicographic may ignore space if food_dist difference 1. Could be okay? Maybe not: a move to food 1 step into tiny trap vs move 2 steps with huge space; lexicographic chooses trap. Need combine. Weighted better.

Maybe use key with buckets: `space_bucket = safe_space // 10`, `food_bucket = -food_dist // 5`. But arbitrary.

Let's keep weighted but with clear priorities.

Candidate features needed:
- fatal, win
- safe_space, total_space
- food_dist
- tail_reachable
- min_enemy_manhattan
- center_dist
- maybe `food_dist_enemy_safe`: if nearest food is also within enemy threat? Not.

Compute min_enemy_manhattan: from new_idx coords to enemy heads. Precompute enemy_heads list coords. Use Manhattan. For 11 snakes, cheap.

Compute center_dist: Manhattan to center (w/2,h/2). Prefer central. But in brawl spawns circle, center may be crowded. Space covers. Small weight.

Potential issue: safe_space counts cells not in fatal threat mask. Threat mask based on current enemy heads; after we move, enemy heads move, threat changes. It may undercount cells adjacent to enemies. Good.

Now, what about other snakes' possible head cells that are also our tail? We may follow tail but enemy could head-on there. Threat mask penalizes.

Could include "body risk" from enemies' possible moves into our body? Not needed.

Let's test some scenarios mentally.

Scenario: Single duel, both length 4, food near. Our bot chooses safe tail reachable. Opponent may try intercept. If opponent adjacent and longer? avoid. If equal, avoid head-on. Good. If opponent tries to cut, our flood fill may see reduced space and avoid.

Potential weakness: Opponent can move into our planned path next turn; we only one-step. But flood fill with other bodies static may not predict. Could be okay.

Could add simple 2-step safety: For each candidate, simulate my move, then assume each enemy moves one step toward nearest food or my head? Too heavy. Maybe not.

Maybe implement "danger flood fill" using enemy distance BFS: compute enemy_reach distances from all enemy heads on blocked grid (excluding my body?); then in my BFS, penalize cells where enemy_dist <= dist_from_me? For food, choose foods where my_dist < enemy_dist. This can avoid contested areas. Let's consider adding.

Compute `enemy_dist_map` multi-source BFS from enemy heads, with obstacles = occ_others? But enemies can pass through their own bodies? For simplicity, blocked = occ_others_static? This includes their bodies, may block them. Maybe use empty grid except walls for threat. Manhattan enough.

Voronoi for food: For each food, compute my BFS distance from current head? We already candidate BFS. Could compute enemy_min_manhattan to food. If my candidate's nearest food has enemy_manhattan <= my food_dist, contested; penalize. But candidate BFS food_dist from new head. Use `food_contest_penalty = max(0, (enemy_food_dist - food_dist))`? If enemy closer, penalty. We can compute for each food: enemy_min_manhattan. When BFS finds nearest food? We only know min distance, not which food. Could during BFS when food cell found, compute contest. But BFS level first food may not be best contest. Simpler: after candidate, compute nearest food by Manhattan? Not path. Maybe not.

Could choose target food before candidate: Score foods by (my BFS dist, enemy manhattan). Then guide moves. But candidate BFS already.

Given time, keep simpler.

Need ensure code only standard library. Use `sys.setrecursionlimit` not needed.

Now, let's think about self-collision due initial overlapping and reverse. Suppose body collapsed [s,s,s], current_dir None. We choose e.g. 'right'. Next state body [s+(1,0),s,s]. current_dir derived right. Good. If we choose 'left' next, opposite invalid; we filter. If body has duplicates but head != neck, current_dir known. If head==neck (maybe after eating? Body example just ate last two overlap, but head distinct from neck unless very short? For length 4 [9,3],[9,4],[9,5],[9,5], head != neck. If length 2 and overlap? maybe not). If head==neck due initial only. Use last_dir.

What if our snake length 3 and body [head,neck,neck] just ate? current_dir head-neck. last two overlap indicates tail stays. Our own masks: tail_stays? For immediate own_full? We decide eating this turn based on new_head food, not current tail_stays. But current tail_stays affects our current body occupancy for other snakes? Not for our own immediate? For own current tail_stays means our tail will not move this turn if we were asked? Wait state reflects after previous turn. If last two overlap, we just ate previous turn, so in the upcoming turn our tail will NOT move. Our movement step: tail does not shrink. Our immediate move: if we move this turn, because tail is stationary, our body after move will be [new_head] + old_body (no pop). But our decision for this turn: If we are currently in grown state, tail does NOT move now. The rule: just ate food previous turn -> next turn tail does not move. So when we move now, tail stays. We must account for own tail not moving this turn! Our previous immediate own_block formulas assumed tail moves unless we eat this turn. But if current state tail_stays (last two overlap), then even if we don't eat this turn, our tail does not move. Important. Similarly for other snakes: if their last two overlap, their tail stays this turn; occ_others_static uses body all, correct. For self, if my tail_stays from previous turn, then moving now: new_body = [new_head] + old_body (no pop), regardless of whether new_head food? If new_head food too, then tail also doesn't move (and length grows), still no pop. So immediate blocked should include old_body all (tail remains). Future space: after this turn, if we ate this turn, tail will stay next turn too (last two overlap in new_body). If we didn't eat but tail stayed due previous, new_body = [new]+old_body; last two of new_body? old tail duplicate remains? Example old [h,n,t,t] (just ate). Move without eating, tail stays: new [new,h,n,t,t]. Last two still overlap? Yes t,t. Does tail stay again next turn? Rule: tail doesn't move only in the turn immediately after eating. If it just stayed because previous eat, and we didn't eat this turn, next turn should tail move or not? Let's parse: When eats, body long +1 (new segment added at tail), so next turn tail does not move. After that turn, if no food eaten, tail moves normally. Body after no-eat move: insert head, no pop? Wait if tail doesn't move, how implement? Usually if grow pending, don't pop tail. Eating sets grow_pending. Next move: insert head, if grow_pending: don't pop, set pending false. If no eat this turn, pending false after move. But body still has duplicate tail? Example before pending: [h,n,t] after eat: new segment added at tail => [h,n,t,t]? Next move no eat: insert new head, don't pop because pending => [new,h,n,t,t], pending false. Next move if no eat: insert head, pop tail => [new2,new,h,n,t]. So after the no-eat turn, last two still overlap, but tail should move next turn because pending consumed. Thus using last two overlap to infer tail_stays for next turn fails for a snake that had pending and didn't eat this turn? But state's last two overlap indicates tail will not move in the upcoming turn (pending). After we move without eating, state next turn will still have last two overlap? Actually if judge body is [new,h,n,t,t], last two overlap. The note "like above last two overlap, means it just ate food, next turn tail not move" would incorrectly imply tail stays again. But maybe judge represents growth differently: When eats, body grows by adding segment at tail, so body last two overlap. Next turn tail doesn't move, but after moving, the overlap resolves? Let's simulate common implementation with body segments as positions, when growing not pop: Before eat: [h,n,t]. Eat food at head: add new segment at tail? If add at tail, body becomes [h,n,t,t] (duplicate). Next turn move: insert new head, if not popping, body [new,h,n,t,t]. Still duplicate. But the duplicate represents two segments at tail; one is new? Next turn if no grow, pop last -> [new2,new,h,n,t]. The duplicate resolved after one move without pop? Wait after pending move, we didn't pop, so duplicate persists. The pending flag is false, but body still duplicate. Next move pop removes one duplicate, so tail cell remains occupied by one segment. So state after pending move has duplicate but no pending. The note says duplicate means just ate, next turn tail not move. That would be wrong for this representation. Maybe judge uses different: When eats, length increases immediately but body positions not duplicate until tail catches? The example in problem: 1号蛇 body [[9,3],[9,4],[9,5],[9,5]], length 4. They say last two overlap indicates it just ate, next turn tail does not move. That is state before next turn. After next turn if no eat, what will body be? They likely implement move as: new head, if not hungry? If length > len(body)? Hmm. They might store length separately and body with duplicates to indicate pending. After move with tail not moving, they might remove one duplicate? Let's derive: If tail does not move, the tail segment remains, but the segment before tail moves into its previous position? Body positions shift: old [h,n,t,t] (two tail segments same). Move no eat with tail stay: head to new, neck to h, third to n, tail(s) stay? There are two segments at t; the last stays, the second-last maybe moves to previous third? Actually segments are linked. If tail doesn't move, the last segment stays; the segment before it moves to its old position? Let's use array insert head, no pop: [new,h,n,t,t]. The second-last t is the old last? It didn't move? In array shift, all existing segments move forward one index in list, but positions: new head at new, old head moves to h? Wait body list positions represent segments. Move: segment i moves to position of segment i-1? If no pop, old tail stays at t, but the segment before tail (also at t due duplicate) moves to old third position n? Hmm if two segments at same cell, one may move, one stays. After move, positions [new,h,n,t,t]? The last t stayed, the second-last t moved to n? But list shows t,t at end, so no. Maybe they don't simulate individual segments; they just add duplicate and pop later. The note might be simplified: duplicate means tail won't move next turn. After that turn, duplicate may still be present? The problem may not require us to infer beyond one turn. For our decision, we only need current turn tail_stays. State duplicate = tail stays this turn. After we choose and if we don't eat, next state maybe still duplicate? If judge's note always duplicate => tail stays, then tail would stay forever until eat? That can't be. They probably use a pending flag encoded by duplicate only for one turn; after move, they might remove duplicate somehow. How? If tail doesn't move, but body length increased, maybe body becomes [new,h,n,t] (length 4) with no duplicate? Let's see: old [h,n,t] length3. Eat: length4, new segment added at tail, but since tail cell same? body [h,n,t,t]. Next turn tail not move: move head, remove first duplicate? Maybe body [new,h,n,t] length4 no duplicate. That makes sense: the extra segment is consumed by not popping? Actually positions: old segments h,n,t plus new tail at t. Move with no pop: head new, neck h, body n, tail t (the new tail?) The old tail moves to n? Then only one t. So [new,h,n,t]. Thus duplicate resolves. If this is judge, state duplicate only means pending for current turn. After move no eat, no duplicate. Then our inference for current turn okay. For future space after current move, if current tail_stays and no eat, new tail unique? Hard. But for one-step decision, immediate safety: if my current tail_stays, tail cell remains occupied, so own immediate block should include all old_body. Our previous own_move_mask (old_body[:-1]) would incorrectly allow moving into unique old tail? But if tail_stays, old tail remains, and if duplicate, old_body[:-1] includes tail cell via body[-2], so still blocked. If duplicate, moving into tail cell blocked anyway. If tail_stays can only be inferred by duplicate, then body[-2]==body[-1], so old_body[:-1] includes tail cell. So own_move_mask is safe even if tail stays because duplicate blocks. Good. If current tail_stays but no duplicate? not possible by state. So immediate okay.

For future space after current move, if current tail_stays and we don't eat, tail might be unique next turn or still duplicate? Not crucial. Our own_space_no_eat_mask = old_body[:-2] may underblock if tail stays? Example old [h,n,t,t], current tail stays. If we move no eat, actual new body maybe [new,h,n,t] (if duplicate resolves) or [new,h,n,t,t]. Future tail behavior? If no eat this turn, tail should move next turn. For space, old_body[:-2]=[h,n], blocks h,n, allows t. If actual new body [new,h,n,t], tail t will move next turn, allow t correct. If actual [new,h,n,t,t] with no pending? tail t will move next turn but duplicate remains, cell t still occupied by second-last, so should block t. Our mask old_body[:-2]=[h,n] allows t, overly optimistic. But duplicate might not persist. Problem note suggests duplicate resolves? Not sure. We can be conservative: if current tail_stays, for future space after no eat, block old_body[:-1]? That includes t via body[-2]? But if tail will move next turn and no duplicate, blocking t is conservative. Maybe safe. Let's adjust own_space_mask for candidate:
- If I will eat this turn: block old_body all (tail stays next turn).
- Else if my current tail_stays: block old_body[:-1]? This includes all except last duplicate but duplicate cell remains via body[-2]; blocks tail cell. Conservative.
- Else: block old_body[:-2] (allow unique new tail).
This may reduce space estimate when just ate, but okay.

Similarly for other snakes' future space, occ_others_static uses body if tail_stays else body[:-1]. If tail_stays, blocks tail cell; conservative for next turn maybe. Good.

Immediate own_block: if eating or current_tail_stays? If current_tail_stays, old_body[:-1] already blocks tail due duplicate; but if length? Use own_full if eating or current_tail_stays? Could mark all old_body. If duplicate, full and move mask same set (because tail duplicate). Use full for safety. So immediate mask: if new_head food or my_tail_stays: own_full_mask else own_move_mask. But if my_tail_stays and old_body duplicate, full same as move mask plus last tail cell already included. okay.

Space mask: if eating: own_full_mask. elif my_tail_stays: own_stay_space_mask = mask old_body[:-1] (or full? If full blocks start? start not in old; block tail cell). else own_short_mask old_body[:-2]. Need build `own_stay_mask` = old_body[:-1]. For duplicate, blocks tail cell. Good.

But if current tail_stays and new_head food, eating mask full; tail stays next turn. okay.

For tail target after candidate: If eating: target old_tail, blocked -> false. If not eating and current_tail_stays: new_body maybe [new]+old_body (if tail stays) or [new]+old_body[:-1]? Which tail target? If tail stays this turn, the tail at end remains old_tail. Next turn tail may move. We can set target = old_body[-1]. But our space mask blocks it (own_stay_mask), so tail_reachable false. Fine.

For normal not tail_stays: target old_body[-2]. Good.

Now, for other snakes, tail_stays inference by duplicate. If initial all stacked, tail_stays true by our inference, but maybe not. occ all body = spawn cell blocked. Conservative. Their possible heads: if tail_stays, own block all body; moving into spawn blocked. If initial, they can move out; spawn cell maybe still occupied by body after move? With all stacked, if tail moves or not, spawn remains occupied by at least one segment, so blocking okay.

Now, possible head directions for enemies with current_dir derived. If body collapsed, unknown. If body head != neck, derive. But if body has duplicate head? Initial all same; unknown. Good.

Need derive enemy current direction for reverse exclusion. If head==neck, use None (all). But if last_dir tracked only for self; not for enemies. Could maybe infer from previous state? Not worth.

Now, let's think about collision with own body when initial stacked. Suppose turn1 body [s,s,s], my_tail_stays True (duplicate). immediate mask full old_body marks s. Candidate new head adjacent not s safe. Good. If we choose direction into s? impossible adjacent same? no. Turn2 body maybe [new,s,s], my_tail_stays True (last two s). immediate mask full marks new? Wait old_body includes new head and s,s. Candidate moving into old head new? That's reverse? current_dir from head new to neck s. Opposite would move into s (neck), blocked. Moving other directions not in old_body. Good. Space mask for tail_stays old_body[:-1]=[new,s], blocks old head and s. Conservative.

Now, BFS neighbor precompute. Need directions order. For current_dir derive from idx: if head - neck == 1 -> right, -1 left, w down, -w up. But if coords not adjacent due duplicate? only if distinct. Use coords to avoid wrap: dx = x_h - x_n, dy = y_h - y_n. If (dx,dy) in deltas. If not, None.

Global variables in bot.py:
```
LAST_DIR = None
GRID_W = None
GRID_H = None
NEIGHBORS = None
DIR_ORDER = ['up','down','left','right']
DELTA = {'up':(0,-1), ...}
OPP = {...}
DIR_INDEX = {...}
```
Need avoid using nonlocal? Use global.

Precompute grid:
```
def ensure_grid(w,h):
 global ...
 if GRID_W==w and GRID_H==h: return
 cells=w*h
 NEIGHBORS = [[] for _ in range(cells)]
 DIR_NEXT = [[-1]*4 for _ in range(cells)] maybe
 for y in range(h): for x in range(w): i=y*w+x; for di,(name,(dx,dy)) ... ni if inside else -1
 COORDS = [(x,y) ...]
```
Direction order consistent. `DIR_NEXT[i][di]` gives next idx or -1. Neighbors maybe list of (di,ni) or just next list. For BFS, need all valid neighbors ignoring direction: `NEIGHBORS[i]` list of ni. For candidate moves, use DIR_NEXT.

Potential memory okay.

decide_main steps in code detail:
```
def decide(state):
 global LAST_DIR
 try:
   turn = state.get('turn',1)
   if turn <=1:
      LAST_DIR = None
   res = main(state)
   if res in DIRS: LAST_DIR = res
   return res
 except Exception:
   return safe_fallback(state)
```
But safe_fallback may need state. If exception in main after globals? Return LAST_DIR or 'up'. Need ensure no exception in fallback. Use nested try.

safe_fallback: Try parse my head, choose first direction inside not opposite LAST_DIR. If none, LAST_DIR or 'up'. But if exception, 'up'.

Main may time out? We should not rely on exception for timeout. Use deadline. If time runs low, return best. But if CPU timeout by judge, bad. Keep margin.

Parsing state:
```
w = int(state['width']); h=int(state['height'])
ensure_grid(w,h)
you = state['you']
snakes = state.get('snakes', [])
my = None
for s in snakes: if s['id']==you: my=s
if my is None: return LAST_DIR or 'up'
food = state.get('food', [])
```
Convert body:
```
def body_to_idx(body): return [y*w+x for x,y in body]
```
Need handle body list of lists. If missing? okay.

Build food_mask bytearray cells; for x,y in food if inside set.
food_indices list maybe for BFS? Food_mask enough.

Build my_body_idx. `my_length = int(my.get('length', len(my_body)))`. `my_health = int(my.get('health',100))`.
`my_head = my_body[0]`.
`my_tail_stays = len(my_body)>=2 and my_body[-1]==my_body[-2]`.
Current dir:
```
current_dir = None
if len(my_body)>=2:
  hx,hy=COORDS[my_body[0]]; nx,ny=COORDS[my_body[1]]
  dx,dy=hx-nx,hy-ny
  for name,(ddx,ddy) in DELTA.items(): if (dx,dy)==(ddx,ddy): current_dir=name
if current_dir is None: current_dir = LAST_DIR
```
But if LAST_DIR opposite? okay.

Candidate directions:
```
candidate_dirs = [d for d in DIR_ORDER if d != OPP.get(current_dir)]
if not candidate_dirs: candidate_dirs = DIR_ORDER[:]
```
But if current_dir None, all. If current_dir known, exclude opposite. However, what if our current_dir derived but actual due previous invalid? We avoid invalid. Good.

Build occupancy others and threat masks:
```
occ_others = bytearray(cells)
threat_fatal = bytearray(cells)
threat_win = bytearray(cells)
enemy_heads = []
max_enemy_len = 0
for s in snakes:
 if s['id']==you: continue
 body=...
 if not body: continue
 length=s.get('length',len(body))
 max_enemy_len=max(...)
 enemy_heads.append(body[0])
 tail_stays = len(body)>=2 and body[-1]==body[-2]
 mark = body if tail_stays else body[:-1]
 for p in mark: occ_others[p]=1
 # possible heads
 # derive enemy dir
 edir=None
 if len(body)>=2 and body[0]!=body[1]: derive
 opp = OPP.get(edir)
 own_block_enemy = bytearray? We can check membership in body set.
```
For enemy possible heads, need know if next cell not in enemy's own immediate block. Could create a set or bytearray for enemy body mark. Since small, for each enemy create `eblock = set(mark)`? Mark length maybe large. Or use a temporary bytearray? For 11 snakes, creating bytearrays each maybe okay. Simpler: `emark_set = set(mark)`; for each dir, if ni != -1 and ni not in emark_set: mark threat. But set of ints length up to 961, okay. For performance, maybe use `emark = bytearray(cells); for p in mark: emark[p]=1` then check. But also occ_others marking. Creating per enemy bytearray 961*10=9k bytes, okay. Time maybe. Use set simpler.

But `mark` for enemy with tail_stays includes all body; if tail unique, excludes tail, so moving into tail possible. Good. If body duplicate, tail cell in mark via previous segment. Good.

Enemy possible heads should also not be wall. If enemy current_dir unknown, allow all; else exclude opposite. But if enemy body collapsed, current_dir None. If edir not None, skip OPP[edir]. However if enemy's actual current direction could be different due invalid? Unknown. Allowing all except derived reverse is okay.

Mark threat:
```
for di, dname in enumerate(DIR_ORDER):
  if edir is not None and dname == OPP[edir]: continue
  ni = DIR_NEXT[head][di]
  if ni == -1: continue
  if ni in emark_set: continue
  if length >= my_length: threat_fatal[ni]=1
  else: threat_win[ni]=1
```
But if multiple enemies, fatal overrides. If a shorter enemy marks win and longer marks fatal same cell, both masks 1. We treat fatal if threat_fatal. Good.

Should we include enemy possible move into occ_others (other bodies)? We currently only exclude enemy's own mark. It may mark cells occupied by other snakes; threat conservative. okay.

Also, if enemy is adjacent and its possible head is my current head cell, threat_fatal marks my current head, but I'm moving away. Not relevant unless candidate new_head there (reverse? excluded maybe). Good.

Build own masks:
```
own_full = bytearray(cells); for p in my_body: own_full[p]=1
own_move = bytearray(cells); for p in my_body[:-1]: own_move[p]=1
own_space_normal = bytearray(cells); for p in my_body[:-2]: own_space_normal[p]=1  # if tail moves
own_space_stay = bytearray(cells); for p in my_body[:-1]: own_space_stay[p]=1  # if current tail stays and no eat
```
Need if len(my_body)<2? but min 3. For `my_body[:-2]` if length 3, one element. If length 2, empty. okay.
If my_tail_stays, immediate mask should be own_full? But own_move also blocks tail due duplicate. Use own_full for simplicity if eating or my_tail_stays. For space if eating: own_full; elif my_tail_stays: own_space_stay; else own_space_normal.

Food set: `food_mask`. For candidate eating = bool(food_mask[new_idx]). But if new_idx is food and also occ_others? immediate unsafe; but if food on enemy tail moving? Food shouldn't. If occ_others[new_idx] true, unsafe even if food. Good.

Immediate blocked check:
```
imm_mask = own_full if (eating or my_tail_stays) else own_move
if occ_others[ni] or imm_mask[ni]: unsafe
```
But if ni is my old tail unique and not eating and not tail_stays, own_move excludes it, safe. If ni is my old tail but my_tail_stays true, own_full includes, unsafe. Good.

Need consider if ni equals an enemy tail that is moving but enemy tail duplicate? occ_others excludes unique tail, includes duplicate via body[:-1]. Good.

Now, if candidate immediate unsafe, we might still keep as fallback with low score. Create list all candidates with features maybe. But to save time, evaluate safe first. If no safe, evaluate unsafe with simple score? Could just choose direction that is not wall and not own body if possible; if all fatal, maybe current_dir. Implement fallback later.

Candidate evaluation:
```
candidates = []
for d in candidate_dirs:
  di=DIR_INDEX[d]; ni=DIR_NEXT[my_head][di]
  if ni==-1: cand unsafe wall
  eating = food_mask[ni]
  imm_mask = ...
  immediate_safe = not occ_others[ni] and not imm_mask[ni]
  candidates.append({...})
```
For safe candidates, run BFS. But if time low, maybe use quick. Need choose best safe.

BFS function inside decide to access globals. Use deadline. Let's implement optimized flood:
```
def flood(start, occ, own_mask, threat, food_mask, target, cells, neighbors, deadline):
    visited = bytearray(cells)
    visited[start]=1
    q = [start]
    dist = 0
    total=0; safe=0; min_food=10**9; tail_found = (start==target)
    while q:
       if time.process_time() > deadline: break
       nxt=[]
       for p in q:
          total += 1
          if not threat[p]: safe += 1
          if food_mask[p] and dist < min_food: min_food = dist
          if p == target: tail_found = True
          for nb in neighbors[p]:
             if not visited[nb] and not occ[nb] and not own_mask[nb]:
                visited[nb]=1
                nxt.append(nb)
       q=nxt
       dist += 1
    return total, safe, min_food, tail_found
```
Potential optimization: Use local variables for speed. Since nested function, okay. `threat` fatal mask. If start threat, safe count excludes start? We might want safe count includes start even if threat? If start fatal, candidate penalized; safe_space maybe 0. Could set `if not threat[p] or p==start: safe +=1` to count start. But if start fatal, safe_space 1 maybe. Not big. Use `if not threat[p] or p == start`. But threat cells beyond start not safe. Good.

Target tail: For candidate:
- If eating: target = -1 (tail unreachable) or my_body[-1] but blocked. Set -1 to false.
- Else if my_tail_stays: target = -1 (conservative) or old_tail? Since own_space_stay blocks tail, false. Set -1.
- Else: target = my_body[-2] if len>=2 else -1.
But if target is -1, tail_found false. If start==target? impossible.

Own mask for BFS:
```
if eating: own_mask_space = own_full
elif my_tail_stays: own_mask_space = own_space_stay
else: own_mask_space = own_space_normal
```
Should we include current my head in own_mask_space? For normal old_body[:-2] includes head if length>2? Example old [h,n,t], old[:-2]=[h], blocks old head. After move, old head occupied by neck, should block. Good. For length 3, blocks h. New body [new,h,n], space from new cannot move into h (neck) immediate next turn? Actually next turn, neck h will move? If we move next turn, old head h becomes occupied by segment behind? Let's see after candidate: [new,h,n]. Next move, if not eat, body [new2,new,h]; cell h becomes tail and vacates. At the start of next turn, cell h is occupied by tail? Wait body [new,h,n], tail n. Cell h is middle segment, not tail. It will move to new next turn, leaving h? Actually segment at h moves to new? No, head moves to new2, segment h moves to new, segment n moves to h. So h remains occupied by tail n after move. For pathfinding from new head at current moment, can we move into h next turn? If we move into h, head would enter h while tail n moves into h? Simultaneous: our head into h, tail n moves to h? That's collision with own body? In snake, you cannot move into your own neck/middle. The only safe body cell is tail if it moves. h is not tail, so blocked. old_body[:-2]=[h] blocks h, good. n (new tail) is passable because tail moves. So correct.

For length 4 old [h,a,b,t], old[:-2]=[h,a], new body [new,h,a,b], new tail b. Block h,a; allow b (tail). Good.

If current tail_stays and no eat, own_space_stay old_body[:-1] blocks h,a,b? old [h,a,b,b] -> [h,a,b], blocks b tail cell conservative. Good.

BFS occ_others includes other bodies after this turn. For future space, other tails that moved this turn may be passable next turn? occ_others excludes unique tails, good. Their heads/neck blocked. Conservative.

Now scoring. Compute features for safe candidates. Need min_enemy_manhattan. Precompute enemy_head_coords list. For candidate ni coords:
```
hx,hy = COORDS[ni]
min_enemy_dist = min(abs(hx-ex)+abs(hy-ey) for enemy heads) if enemies else 99
center_dist = abs(hx-cx)+abs(hy-cy)
```
If no enemies, min_enemy_dist large.

Score formula. Let's refine with possible values.
- safe_space up to 961, total up to 961.
- food_dist up to maybe 62. If unreachable INF, set 200.
- tail_reachable bool.
- fatal bool.
- win bool.
- health 0-100, turns_left = max_turns - turn.
Weights:
```
turns_left = max(0, int(state.get('max_turns',500)) - turn)
health = my_health
score = 0
if fatal: score -= 10_000_000
if win: score += 10_000  # small
if tail: score += 1_000_000 if health > 35 and turns_left > 30 else 300_000
space_val = safe_space * 60 + total_space * 5
# trap penalty: if safe_space < max(8, my_length): score -= 800_000
if safe_space < max(6, min(50, my_length*2)): score -= 500_000 ?
score += space_val
food_eff = food_dist if food_dist < 900 else 200
# food weight: base 1000; urgency multipliers
fw = 800
if health < 60: fw *= 2
if health < 35: fw *= 2
if turns_left < 40: fw *= 2
if turns_left < 15: fw *= 2
if not i_am_longest: fw *= 1.5
score -= food_eff * fw
# If food unreachable, food_eff=200, penalty maybe 200*800=160k normal, okay.
# enemy proximity: prefer farther if not hungry. min_enemy_dist max 60. score += min_enemy_dist * 50
score += min_enemy_dist * (20 if health>50 else 5)
# centrality small: score -= center_dist * 10
score -= center_dist * 5
```
Tail bonus 1M dominates space/food unless health low or endgame. If health <35 tail bonus 300k, food weight 800*4*... maybe 3200*200=640k if unreachable or dist 100 =>320k. Food can override. Trap penalty 500k can override tail if safe_space tiny. Need threshold. If safe_space < my_length maybe definitely trapped. Use `if safe_space < my_length: score -= 1_500_000` maybe. But if no alternatives, still choose. Maybe `if safe_space <= max(4, my_length//2): score -= 700_000`.

Maybe tail bonus too high: It may ignore food forever if tail reachable, causing starvation when food path requires temporarily losing tail reachability. But classic safe snake can often eat while maintaining tail reachability. If not, maybe need take risk before health low. Health low reduces tail bonus. Good.

Could add if `food_dist <= 3` and health<80, food weight may overcome? Tail bonus 1M, food diff maybe 10*800=8k, no. So always tail. Only health<35 tail 300k, food weight maybe 3200, dist 100 =320k tie. So it may wait until health 35 to chase food if tail safe but food far. That's okay? Could starve if food unreachable while tail-chasing but health declines; then chase. Might be too late with opponents. Maybe reduce tail bonus to 200k normal. Space weight 60*961=57k. Food weight normal 800*100=80k. Tail bonus 200k still strong. Health<60 fw=1600 ->160k. Health<35 fw=3200 ->320k. Let's set tail_bonus = 300k if health>50 else 100k. Then food can override when urgent. But tail important. Maybe 250k.

Let's set:
```
tail_bonus = 250_000 if health > 45 and turns_left > 40 else 80_000
trap_penalty = 400_000 if safe_space < max(4, my_length) else 0
space_weight = 80 safe + 10 total (max ~85k)
food_weight base = 1200, health multipliers, endgame.
```
Normal: tail 250k > space+food (food dist 50*1200=60k). Good. Health 40: tail 80k, fw=2400, food dist 20 diff 48k; food can influence. Health 20: fw=4800, food dist 10=48k, tail 80k still; but if food unreachable penalty 200*4800=960k, so choose reachable.

If i_am_longest? `max_enemy_len` maybe. In duel if no enemies, i_am_longest True. If shorter, fw*1.5. If longer and health high, maybe still eat to maintain lead. okay.

Fatal penalty 5_000_000. Trap penalty 400k. If fatal candidate but tail and food, still avoided if nonfatal. If all fatal, choose best among fatal.

Need maybe if `safe_space == 0` because start threat but total_space large; safe_space count includes start if we do `not threat or p==start`, so at least 1. Good.

Tie-breaking: Add small random `random.random()*10` or use direction order. Since random seeded, okay. But deterministic might be fine. Add `score += random.random()` maybe not if random module imported. But if score differences large, no effect. For equal, random helps avoid predictability? Opponents can't adapt? Maybe. Use `random.random()` but not necessary. Could cause non-determinism across judge seeds; okay.

Now, if no immediate safe candidates. Need choose least bad. Could evaluate all candidates with immediate_safe false. Maybe choose direction that is not wall and not own body if possible? But all are fatal. We can choose move that maximizes potential (maybe head-on where we longer) or current_dir. Simpler: For all dirs (including opposite? actual maybe), compute if inside and not occ_others? If none, return LAST_DIR or current_dir. But if all immediate unsafe, maybe moving into enemy head where we longer could kill them and survive? If new_head in occ_others due enemy current head, static body collision? Actually moving into enemy current head is collision with neck, die regardless of length. So no. If new_head is possible enemy head fatal, not static unsafe; those are considered safe immediate but fatal risk. If no immediate safe due walls/body, likely die. Choose direction with largest open neighbor? Could use quick flood without own mask? Not important.

Implement:
```
safe_candidates = [c for c in candidates if c['immediate_safe']]
if not safe_candidates:
  # try any direction not wall and not occ_others (ignoring own? maybe reverse)
  for d in candidate_dirs: if inside and not occ_others[ni]: return d? (will collide own maybe)
  return current_dir or LAST_DIR or 'up'
```
But if own body blocks all but reverse, returning reverse actual current may be only. Use current_dir if known.

Maybe if all immediate unsafe, choose direction not opposite with maximum distance to wall? fallback.

Need ensure candidate_dirs excludes opposite; but if current_dir leads certain death and turning reverse invalid (so actual current) no help. If all non-reverse unsafe, maybe return current_dir. okay.

Now, can we add special duel logic? Perhaps use a simple 1-ply opponent response to avoid being killed by opponent's best move. Our fatal risk already. Maybe add "opponent can move into our current head"? We avoid moving into their possible heads, but they might move into our current head if we move away? That would kill them? Our current head becomes neck, so if enemy moves into our old head, they collide with our neck and die, not us. Good.

What about opponent moving into cell behind our new head (our neck) causing collision? They die. Not threat.

What about opponent body moving into our new head because their neck moves? Our static occ_others includes their current head (neck after move), so we avoid. Good.

Now, possible issue: In head-on collision, if two heads enter same cell and one longer survives, the surviving head is in cell, but what about body collisions with necks? The rule specifically heads same cell resolved. If I move into enemy possible head cell, and enemy moves there, only heads same cell; no neck in that cell unless some body. If cell was enemy's current tail moving out, okay. Our threat model okay.

Now, let's consider food and growth affecting tail in same turn. If candidate eats, own immediate mask full. But if new_head is food and also my current tail unique? Can food be on my tail? Probably no. If it were, immediate mask full blocks, but maybe tail moves and food could be eaten? Rules food appears empty, so no.

Now, test initial turn. State body [[3,3],[3,3],[3,3]], health100, food. ensure grid. my_tail_stays True (last two equal). own_full marks spawn. Candidate dirs all (current_dir None). For each ni adjacent not spawn, immediate safe. own_space for eating? if not food and my_tail_stays => own_space_stay old_body[:-1] marks spawn (all same). BFS blocked occ others + spawn. Space from adjacent. Threat maybe enemy possible heads. Score chooses based on space/food. Good. Might choose toward center/food. Need set LAST_DIR to chosen. Next turn derive current_dir.

Now, think about health/hunger. Health decreases each turn; state health given. If we ate previous turn, health 100. If health low, need food. Food distance BFS from candidate after move. If food reachable only by moving into fatal risk, and health critical, score may still avoid fatal due -5M. Maybe starve. But if all safe moves no food, eventually fatal risk necessary. Fatal penalty huge means only if all candidates fatal. If there is safe but no food, it will choose safe until dead. Could be bad if only risky path to food. But survival first; maybe okay. Could reduce fatal penalty when health very low? If health <10, taking head risk may be better than starvation. But head risk likely death; starvation death in <=10 turns. If risk maybe 50% survival. Could allow. We can make fatal penalty scale with health: if health <=15, penalty 500k not 5M, so food may override. But strong opponents, risky. Ranking survival; dying by risk sooner than starvation? If starvation inevitable, risk worth. Let's adjust: `fatal_penalty = 5_000_000 if health > 20 else 1_000_000`. Tail/trap weights similar. If health critical and food close fatal, may take. But if safe move exists but leads starvation later, maybe still not. Could also if turns_left > health and no reachable food from safe moves, increase food urgency. Hard.

Maybe compute if any safe candidate has reachable food (food_dist < INF). If none and health < 50, consider fatal candidates. Our scoring with fatal penalty may still choose safe because safe no food penalty 200*fw maybe less than fatal penalty. If health critical, set fatal penalty lower. Good.

Now, endgame: If max_turns near, length matters. If we are alive and shorter, may need food risks. Increase food weight, reduce tail bonus. If turns_left < 10, survival to turn limit more important than food? If can survive, length tie. But if not longest, need grow. Risk fatal still avoid unless starvation. okay.

Now, possible optimization: Since BFS per candidate uses `time.process_time()` inside loops, overhead. Could skip deadline check inside BFS for speed, relying small. But to avoid timeout, maybe check per candidate before BFS. BFS over 961 cells *4 = 4k, no problem. We can omit per-level time check or keep lightweight. 50ms, Python function calls okay. Use local `process_time = time.process_time` maybe.

Let's estimate CPU: Parsing bodies total length up to 961. Building masks loops ~ few thousand. BFS 4*961*4 neighbor checks ~15k. All in Python <10ms. Good. No need deadline inside BFS, but include if turn large? Maybe okay. However if board 31x31 and many snakes long, parsing sets maybe. Still <50ms. But we also have enemy possible heads sets. Fine. Keep deadline check outside maybe. To be safe, in BFS while q: if `process_time() > deadline: break` per level (max 60) small overhead.

Now, code structure. Need ensure no external imports except standard: `import random, time`. Could use `math` not needed. `collections` not needed if list queue. Use `sys`? not needed.

Potential bug: `state['snakes']` length field may be not int? okay. `body` list may contain tuples? Example lists. Use `x, y = p` works for list/tuple.

Potential bug: If food list contains coordinates outside? ignore.

Potential bug: If board size changes between calls? In one game fixed. ensure_grid resets if different. Globals from previous turn same. If turn==1 reset LAST_DIR. Good.

Potential bug: Random module seeded; using random.random in score may require import random. okay.

Potential bug: Returning direction not in candidate_dirs due fallback? Ensure.

Now, let's think about more advanced strategies: Could implement "avoid possible enemy head cells" as hard if longer? Already fatal penalty. But what about enemy possible head where enemy length < mine: win. If we move there, and enemy chooses, we survive and enemy dies, good. But if enemy doesn't, no effect. Could be used aggressively to intercept. Score win bonus 10k. Maybe if enemy is shorter and food near, okay. But moving into adjacent cell of shorter enemy could be safe if head-on, but if they move elsewhere, we might be close. Fine.

Could we deliberately head-on with equal length? Both die. In pairwise, if both die same turn same length, tie? Maybe not worth. Fatal includes equal. If only one enemy and both die, maybe tie 0? Avoid.

Now, consider multiple snakes and dead snakes disappear. If an enemy dies, their body disappears immediately, opening space. Our static occ includes them; conservative. If we can cause longer enemy to die by collision with us? If we are longer and move into possible head, win bonus. Could accelerate. But not essential.

Now, test specific rule: "尾巴在第 1 步已经缩回，所以可以跟着别人的尾巴走；但刚吃过食物的蛇尾巴不动。" Our occ_others excludes unique tails, includes duplicate tails. Good. But what about a snake that just ate and has duplicate tail, but the duplicate cell may still be safe if two segments? Tail doesn't move, so unsafe. Good.

Now, possible issue: For other snakes, if tail_stays false but body[-1]==body[-2] due initial? We treat tail_stays true. Could mark tail cell blocked. Conservative. If it's actually moving but duplicate remains, maybe still blocked. okay.

Now, need maybe track our own last direction more reliably. Suppose state turn increments but our body head==neck due just ate? Could current_dir derived None and LAST_DIR from previous. Good. If our process restarted mid-game? Not; new process per game. If exception fallback maybe last_dir not updated? okay.

Now, think about if we choose direction but judge says reverse invalid and continues original. We avoid opposite of derived current_dir. But if derived current_dir wrong due body duplicates? Example body [new,s,s], head new, neck s, direction correct. If body head==neck (collapsed), LAST_DIR maybe correct. If LAST_DIR None, all allowed. Good.

Now, possible problem: Our candidate_dirs excludes opposite of current_dir, but if current_dir is None and LAST_DIR set? We set current_dir = LAST_DIR if derive None. So exclude opposite of last_dir. If body collapsed but we moved last turn, last_dir actual. Good. If body collapsed turn1, no exclude.

Now, consider if we are forced to continue original direction due previous timeout? Our LAST_DIR may not match actual if judge forced straight. But timeouts rare. If invalid return? We avoid. If fallback returns last_dir maybe okay.

Now, let's consider implementing a simple "panic food search" if health low and no safe reachable food. Could choose candidate with minimal food_dist even if fatal. Score handles.

Now, maybe we can improve by using path distance to food from current head rather than candidate BFS. Candidate BFS food_dist from new head. If food is behind, moving away increases. Good.

Now, possible bug in BFS food distance: It finds first food at current level but doesn't stop; min_food set. If food at start? Could happen if head on food? At turn start, if previous turn ate, head maybe on food? Food consumed, new food elsewhere. State food should not include head. If start food, min_food=0. okay.

Now, tail_reachable: BFS target tail. But BFS blocked includes own_space mask; if target passable, reachable. However BFS may reach tail cell through cells that are threat_fatal; tail_reachable true but dangerous. Score safe_space penalizes. okay.

Now, code for scoring candidates. Need store best. For safe candidates, compute score. If time runs low before evaluating all, choose best so far or first safe. Could implement loop with deadline check. But likely fine. Add:
```
if process_time() > deadline:
   break
```
If break and best_candidate None, choose first safe dir quick.

Now, fallback safe_fallback. Should not call main if state invalid. Implement robust:
```
def fallback(state, err=None):
 try:
   w=state['width']; h=state['height']; you=state['you']
   for s in state['snakes']: if s['id']==you: head=s['body'][0]
   # prefer last_dir if next inside? maybe
   if LAST_DIR and inside: return LAST_DIR
   for d in DIR_ORDER: nx... if inside: return d
 except: pass
 return 'up'
```
But if LAST_DIR leads into wall, maybe choose inside. Could quick check walls only. Not bodies. okay.

Need global LAST_DIR updated in decide even if main fallback? In decide wrapper:
```
result = None
try: result = decide_main(state)
except Exception: result = fallback(state)
if result not in DIR_INDEX: result = LAST_DIR or 'up'
LAST_DIR = result
return result
```
But if result invalid and we set LAST_DIR to invalid? ensure. If fallback returns LAST_DIR maybe. Use `if result in DIR_INDEX`.

But if exception occurs, LAST_DIR might not reflect actual if result fallback not evaluated? okay.

Now, potential issue with using global GRID arrays in fallback before ensure_grid. fallback can just use width/height and deltas without precompute.

Now, let's think if code can be further strengthened with "simulate candidate one step and re-evaluate threat after enemies best respond". Maybe not necessary but could add small 1-ply for duel. Let's see if we can add a special `duel_adjust` without risking bugs.

In single duel, we can compute for each safe candidate a worst-case opponent immediate outcome: For each possible enemy move (legal), simulate positions after both moves. If I die in any, penalty; if enemy dies, bonus. But our fatal threat already captures head-on if enemy moves into my new head. It doesn't capture if enemy moves into a cell that causes me to collide with their body? My new head static safe against their body after move (occ_others). If enemy moves, their body after move includes old body[:-1] plus new head. My new head could equal their new head (head-on) or their old body (static). We avoid old body. If enemy moves such that their new head becomes adjacent, no immediate death. So one-ply mostly head-on. Could compute if enemy can move into my new head and length >=, fatal. Already.

Could compute if enemy can move into food and grow, becoming longer, affecting future. Not immediate.

Maybe implement "distance to enemy head" using BFS not Manhattan to avoid walls/bodies. But Manhattan okay.

Now, think about board 31x31 with 11 snakes. Many snakes along border. Initial choose inward? Our scoring: center_dist small weight, space maybe inward larger. At borders, space outside wall low; chooses inward. Good.

Potential issue: In brawl, many snakes may converge on center; our bot might avoid crowded center due threats and space, maybe survive. Good.

Now, let's consider starvation in large board. Food count 12, snakes 11. Health 100. Our bot will chase nearest reachable food if tail reachable. It may avoid contested food due threats. Should eat enough. If it tail-chases too long, health declines. We set tail bonus normal 250k, food weight base 1200. Food distance difference of 50 =>60k, not override tail. It will only choose food if tail reachable for that move. If moving toward food makes tail_reachable false, it avoids until health low. Could starve if every path to food temporarily loses tail reachability. In open board, there should be moves maintaining tail. With opponents, maybe not. Health low tail bonus 80k, food weight 2400/4800, can override. Good.

Maybe tail_reachable one-step is too strict: A move may not immediately see tail reachable but leads to food and safe later. It will avoid. Survival okay.

Now, possible improvement: If no candidate tail_reachable and health high, choose max space. If space large, may later tail reachable. Good.

Now, let's test simple empty board length3. my_tail_stays true initial, tail_reachable false. Scores based on space/food. It may move toward food, maybe into center. As body unfolds, tail_reachable becomes true. Good.

Now, need ensure own_space_normal for length 3 after not tail_stays. Suppose body [h,n,t], not tail_stays. own_space_normal old[:-2]=[h]. BFS from new head blocks h, allows n (new tail). Tail target = n. BFS can reach n? From new head, neighbors include h? blocked, maybe other cells. To reach n, need path around. In a straight line, new head at ahead of h, n behind h. Cannot reach n without passing h (blocked), so tail_reachable false. In classic snake, after moving straight, tail is behind body, not reachable unless loop. That's correct. If turning, maybe reachable. Good.

Now, consider if candidate move is turning such that new head adjacent to tail n, BFS can reach tail. Good.

Now, possible issue: BFS blocked includes occ_others, which includes other snakes' current heads (occupied by neck). For tail reachability, this may block paths. Conservative.

Now, let's think about head-on with multiple enemies and length. If my_length > enemy_length, threat_win mask. If enemy shorter possible head, we don't fatal. But if there are two shorter enemies and both move into same cell with me, head collision: longest survives. If I am longest, survive. If multiple longer? fatal. Good.

Now, maybe we should consider that if I move into food, my length increases before elimination, but threat comparison current length okay. If enemy shorter by 1 and not sharing food, but I eat and become longer; no head-on unless same cell. If same cell, both eat and relative same. okay.

Now, code details for masks. Bytearray OR not needed; BFS checks two masks. But threat mask safe count uses threat_fatal. For immediate check, `if occ_others[ni] or imm_mask[ni]`. Good.

BFS neighbor checks: `if not visited[nb] and not occ_others[nb] and not own_mask[nb]:`. If own_mask is bytearray, indexing returns int. Good. Need local variables for speed.

Potential bug: If start is blocked by own_mask due candidate immediate safe? Shouldn't. But if own_space mask includes new_head? Could happen if new_head in old_body[:-2] but immediate unsafe; safe candidates exclude. If my_tail_stays and own_space_stay old_body[:-1] maybe includes new_head? If immediate safe with own_full? no. Good.

Now, need compute `eating = bool(food_mask[ni])`. But if food_mask is bytearray, returns int. okay.

Now, possible issue: Food may be under a snake body in state? If so food_mask cell blocked; BFS won't reach. But immediate candidate could move into food if tail safe? If occ_others blocks, unsafe. okay.

Now, let's consider using `random` for tie. At end, if best_dir None, choose fallback. If candidates with scores, choose max. Add small random to score: `score += random.random()`. But if exception in random? no. Could make result non-deterministic; okay. Maybe use `random.random()*100`? Differences large; only ties. Use `score += random.random()`.

Now, let's think about potential hidden judge self-check: 12 games vs baseline. Need no errors. Our code wrapped try. Should pass. Need ensure return direction exactly strings lower-case. Good.

Now, maybe CPU time: Precompute neighbors first turn within 1s. 31x31 961 cells *4 trivial. BFS per turn maybe okay. But Python in sandbox 50ms CPU. Need optimize enough. Let's approximate: Each BFS level loops all visited cells; for 4 candidates full 961 => 3844 cells, neighbor avg 3.5 => 13k checks. Each check Python ifs. Plus parsing maybe 1k. Should be <5ms. Good. If we create sets for each enemy body, 10* length maybe 10k, okay.

Could further optimize enemy possible heads: Instead of set(mark), use occ_enemy bytearray? But set membership okay. For long bodies, set construction O(length). Total length <=961, so fine. For each enemy, `emark = set(mark)`; mark list maybe body or body[:-1]. Good.

Now, possible bug: `body_to_idx` for each snake each turn. Could cache? Not needed. But if many snakes length large, conversion O(961). okay.

Now, let's detail code functions.

```
import random, time

DIR_ORDER = ['up','down','left','right']
DELTA = {'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
OPP = {'up':'down','down':'up','left':'right','right':'left'}
DIR_INDEX = {d:i for i,d in enumerate(DIR_ORDER)}
GRID_W = 0; GRID_H=0; CELLS=0; NEIGHBORS=[]; DIR_NEXT=[]; COORDS=[]
LAST_DIR=None

def ensure_grid(w,h): ...
```
In ensure_grid, need fill DIR_NEXT as list of lists of 4 ints. Could also create `NEIGHBORS` as tuple of valid nexts. Use local DIR_ORDER and DELTA. For each cell:
```
DIR_NEXT[i] = [ni0,ni1,ni2,ni3]
NEIGHBORS[i] = [ni for ni in DIR_NEXT[i] if ni!=-1]
```
Coordinates: `COORDS[i]=(x,y)`.

Direction derivation function:
```
def direction_between(head, neck, w):
 if head==neck: return None
 dx = COORDS[head][0]-COORDS[neck][0]
 dy = COORDS[head][1]-COORDS[neck][1]
 for d,(ddx,ddy) in DELTA.items(): if dx==ddx and dy==ddy: return d
 return None
```
Could precompute `DELTA_TO_DIR = {(0,-1):'up',...}` for speed.

Body conversion:
```
def to_idx(body,w):
  out=[]
  for p in body:
    x=p[0]; y=p[1]
    if 0<=x<w and 0<=y<h: out.append(y*w+x)
  return out
```
Need h global? pass. If invalid skip; but body should valid. If skip, could mess length. Maybe assume valid.

Flood function nested or top-level? Top-level with parameters for speed. But needs deadline. Define top-level `flood(start, occ, own_mask, threat, food_mask, target, cells, neighbors, deadline)`.

Potential optimization: Use `while q:` with index instead of level to avoid next lists? Need distance. Could store parallel `dist` array? Level lists okay. But creating many lists. Alternative queue list with distances in separate list: `q=[start]; d=[0];` but memory. Level lists fine. Max levels ~62, total appended cells 961.

BFS code:
```
def flood(...):
    visited=bytearray(cells)
    visited[start]=1
    current=[start]
    dist=0
    total=0; safe=0; min_food=9999; tail_found = (target != -1 and start==target)
    process_time=time.process_time
    while current:
        if process_time() > deadline: break
        nxt=[]
        for p in current:
            total += 1
            if (not threat[p]) or p == start: safe += 1
            if food_mask[p] and min_food == 9999: min_food = dist
            if target != -1 and p == target: tail_found = True
            for nb in neighbors[p]:
                if not visited[nb] and not occ[nb] and not own_mask[nb]:
                    visited[nb]=1
                    nxt.append(nb)
        current=nxt
        dist += 1
    return total, safe, min_food, tail_found
```
If min_food already found, still check food? Could skip if min_food==9999 for speed. Good.
Note: If food at start, min_food=0. If target start, tail_found true.

Now, scoring function maybe inside decide_main to access state. But can compute.

Let's write decide_main pseudo:
```
def decide_main(state):
    global LAST_DIR
    turn = int(state.get('turn',1))
    if turn <= 1: LAST_DIR = None
    w=int(state['width']); h=int(state['height']); ensure_grid(w,h)
    you=state['you']
    snakes=state.get('snakes',[])
    my=None
    for s in snakes:
       if s.get('id')==you: my=s; break
    if my is None: return LAST_DIR or 'up'
    my_body_raw=my.get('body',[])
    if not my_body_raw: return LAST_DIR or 'up'
    my_body=[...]
    my_length=int(my.get('length', len(my_body)))
    my_health=int(my.get('health',100))
    max_turns=int(state.get('max_turns',500))
    turns_left=max(0,max_turns-turn)
    food=state.get('food',[])
    food_mask=bytearray(CELLS)
    for p in food: ... food_mask[idx]=1
    # current dir
    current_dir=None
    if len(my_body)>=2:
       current_dir=direction_between(my_body[0],my_body[1])
    if current_dir is None: current_dir=LAST_DIR
    candidate_dir_names=[d for d in DIR_ORDER if not current_dir or d != OPP[current_dir]]
    if not candidate_dir_names: candidate_dir_names=DIR_ORDER[:]
    my_head=my_body[0]
    my_tail_stays = len(my_body)>=2 and my_body[-1]==my_body[-2]
    # masks
    own_full=bytearray(CELLS)
    for p in my_body: own_full[p]=1
    own_move=bytearray(CELLS)
    for p in my_body[:-1]: own_move[p]=1
    own_space_normal=bytearray(CELLS)
    for p in my_body[:-2]: own_space_normal[p]=1
    own_space_stay=bytearray(CELLS)
    for p in my_body[:-1]: own_space_stay[p]=1
    # others
    occ_others=bytearray(CELLS)
    threat_fatal=bytearray(CELLS)
    threat_win=bytearray(CELLS)
    enemy_head_coords=[]
    max_enemy_len=0
    for s in snakes:
       if s.get('id')==you: continue
       body_raw=s.get('body',[])
       if not body_raw: continue
       body=[...]
       length=int(s.get('length', len(body)))
       max_enemy_len=max(max_enemy_len,length)
       head=body[0]
       enemy_head_coords.append(COORDS[head])
       tail_stays = len(body)>=2 and body[-1]==body[-2]
       mark = body if tail_stays else body[:-1]
       for p in mark: occ_others[p]=1
       # possible heads
       edir = direction_between(body[0], body[1]) if len(body)>=2 else None
       opp_dir = OPP.get(edir) if edir else None
       emark_set = set(mark)
       for di,dname in enumerate(DIR_ORDER):
          if opp_dir and dname==opp_dir: continue
          ni=DIR_NEXT[head][di]
          if ni==-1: continue
          if ni in emark_set: continue
          if length >= my_length: threat_fatal[ni]=1
          else: threat_win[ni]=1
    # center
    cx=w/2? Use (w-1)/2. center_dist integer? Use float? For score, use abs(hx*2 - (w-1)) etc to avoid float.
```
Center distance: `center_score = abs(hx*2 - (w-1)) + abs(hy*2 - (h-1))` (twice Manhattan). Good.

Candidate loop:
```
    deadline = time.process_time() + (0.8 if turn==1 else 0.04)
    best_dir=None; best_score=-10**18
    safe_exists=False
    for d in candidate_dir_names:
       di=DIR_INDEX[d]; ni=DIR_NEXT[my_head][di]
       if ni == -1: continue
       eating = bool(food_mask[ni])
       imm_mask = own_full if (eating or my_tail_stays) else own_move
       immediate_safe = not occ_others[ni] and not imm_mask[ni]
       if not immediate_safe:
          continue
       safe_exists=True
       # space mask
       if eating: own_space=own_full; target=-1
       elif my_tail_stays: own_space=own_space_stay; target=-1
       else: own_space=own_space_normal; target=my_body[-2] if len(my_body)>=2 else -1
       total_space, safe_space, food_dist, tail_found = flood(ni, occ_others, own_space, threat_fatal, food_mask, target, CELLS, NEIGHBORS, deadline)
       fatal = bool(threat_fatal[ni])
       win = bool(threat_win[ni])
       hx,hy=COORDS[ni]
       min_enemy=99
       for ex,ey in enemy_head_coords:
          md=abs(hx-ex)+abs(hy-ey); if md<min_enemy: min_enemy=md
       center = abs(hx*2-(w-1))+abs(hy*2-(h-1))
       # score
       i_am_longest = my_length >= max_enemy_len
       health = my_health
       score = 0.0
       fatal_penalty = 5_000_000 if health > 20 else 1_000_000
       if fatal: score -= fatal_penalty
       if win: score += 20_000 if i_am_longest else 5_000
       tail_bonus = 250_000 if health > 45 and turns_left > 30 else 80_000
       if tail_found: score += tail_bonus
       # trap penalty
       min_space = max(4, min(80, my_length))
       if safe_space < min_space:
           score -= 400_000
       score += safe_space * 80 + total_space * 10
       if food_dist >= 9999: food_eff = 200
       else: food_eff = food_dist
       fw = 1200
       if health < 60: fw *= 2
       if health < 35: fw *= 2
       if turns_left < 40: fw *= 2
       if turns_left < 15: fw *= 2
       if not i_am_longest: fw = int(fw * 1.5)
       score -= food_eff * fw
       score += min_enemy * (30 if health > 50 else 10)
       score -= center * 5
       score += random.random()
       if score > best_score: best_score=score; best_dir=d
    if best_dir: LAST_DIR=best_dir; return best_dir
    # if no safe candidate, fallback
```
Need update LAST_DIR in wrapper, but can also here. Avoid double. decide wrapper sets. But if main returns, wrapper sets. No need inside.

Potential issue: `target=-1` if eating; tail_found false. But if tail_found false, no tail bonus. Good.

If my_tail_stays and not eating, target=-1; tail bonus false. This may be too harsh for one turn after eating. But tail unreachable due duplicate; okay.

Could set target = my_body[-1] and own_space_stay blocks it, false. same.

Now, fallback if no safe candidate:
We can evaluate all candidate directions with a quick score: inside, not occ_others maybe, not wall. But immediate_safe false due own body or occ. If no safe, maybe choose direction not wall with max space ignoring own? Could just return current_dir if in candidate_dirs else candidate_dirs[0]. But if current_dir leads into wall, candidate_dirs includes it? current_dir is not opposite, so yes. If current_dir unsafe, maybe turning unsafe too. Choose direction with smallest collision? Let's implement a quick fallback:
```
# try directions that are inside and not occ_others (ignoring own body), preferring not own_full
best=None; best_val=-1
for d in candidate_dir_names:
  ni=DIR_NEXT[my_head][DIR_INDEX[d]]
  if ni==-1: val=-1000
  else:
    val=0
    if not occ_others[ni]: val+=10
    if not own_full[ni]: val+=5
    if not threat_fatal[ni]: val+=2
    val += random.random()
  if val>best_val: best_val=val; best=d
if best: return best
return current_dir or LAST_DIR or 'up'
```
But if ni in own_full, moving into own body fatal; but all fatal. okay. If candidate_dirs empty, use DIR_ORDER.

Need maybe if current_dir is None and LAST_DIR None, fallback choose toward center/food. But okay.

Now, potential issue: The wrapper sets LAST_DIR to returned direction. If main fallback returns opposite of current_dir? candidate_dirs excludes. Good.

Now, need ensure `state` maybe has snakes with body length 0? not. If body raw coordinates not lists? okay.

Now, let's think about if our own body conversion skips invalid coordinates and length becomes 0. Then fallback. okay.

Now, could we further improve by considering "health of enemies"? If enemy health low, they may die soon; not important. Could avoid longer enemies. We use length.

Now, possible hidden judge nuance: "生命值降到 0：饿死" after hunger step before eating. Health starts 100, decreases each turn, eat resets. If health 1, after hunger becomes 0, then eat? Order hunger before eat: If health 1 and moves onto food, health becomes 0 then eat resets to 100? The order: 2 hunger减1, 3 eat. If health 1, reduces to 0, then eat? It says health降到 0饿死 in elimination after eat? Elimination step after eating. If health 0 but ate, health回满, so survives. So health 1 can eat. Our urgency okay.

Now, possible nuance: If two snakes heads same cell and one longer, longest survives; if the longer also collided with body? Elimination simultaneous; maybe body collision also. If head same cell and body there? rare. Our static avoids body.

Now, let's test some scenarios manually.

1. Turn1 15x15 at (3,3), enemy (11,11), food maybe (2,2),(12,9),(7,7). candidate_dirs all. occ_others enemy spawn mark maybe all body stack at (11,11). threat_fatal enemy possible heads around (11,11), far. BFS space: near corner, moving right/down has more space than up/left. Food distance. Chooses likely right/down toward center. Good.

2. Snake near wall with enemy behind. Space chooses inward.

3. Head-on adjacent equal length: My head (5,5), enemy head (5,6), current_dir maybe up? Candidate moving down into enemy head: ni enemy head, occ_others includes enemy head? enemy body[:-1] includes head, yes immediate unsafe. Moving left/right/up: if up cell (5,4) is enemy possible head? enemy head (5,6), possible heads (5,5),(4,6),(6,6),(5,7); not (5,4). safe. Good.

If enemy head (5,4), my head (5,5), moving up into (5,4) occ_others unsafe. Moving down (5,6) enemy possible? enemy possible (5,5),(4,4),(6,4),(5,3); not. safe. Good.

If enemy head diagonal (4,4), my head (5,5), moving up-left? My moves up (5,4) is enemy possible? enemy possible (4,5),(3,4),(5,4),(4,3); yes fatal if length>=. So avoid moving adjacent into possible head. Moving right/down safe. Good.

Now, issue: Enemy possible heads includes cells blocked by occ_others (other bodies). If enemy head diagonal and cell (5,4) is occupied by another snake body, enemy couldn't move there, but we avoid. Conservative.

Now, possible issue: We mark threat_fatal for enemy possible heads based on enemy length >= my_length. But if I will eat food this turn, my effective length in head-on if same food? If new_head food and enemy moves there, both grow, relative same. If enemy length == my_length-1, not fatal. If enemy length == my_length, fatal. okay. If I eat food and enemy moves into my new head but food maybe not? same cell is food. okay.

Now, consider if I am longer and moving into possible head of shorter enemy. threat_win. We add bonus. But if there is also a longer enemy possible same cell, threat_fatal set. fatal dominates. Good.

Now, should we mark threat_fatal for enemy possible heads even if enemy would have to reverse? We exclude derived opposite. If enemy body collapsed, unknown. If derived wrong due previous invalid, maybe. Conservative.

Now, think about using health to adjust fatal penalty. If health <=20, fatal penalty 1M. Trap penalty 400k, tail 80k, food weight high. A fatal move with food dist 0 could score -1M + maybe -0 + space, safe nonfatal no food penalty 200*fw (fw maybe 9600?) = -1.92M, so fatal chosen. Good. If safe food far, maybe fatal chosen. Reasonable.

Now, maybe if turns_left very small (e.g., 2), survival to limit more important than food; fatal penalty should remain high regardless health. If health >20, high. If health low but only 2 turns, starvation maybe not if health >2. Could avoid fatal. Our health fatal penalty low only if health<=20. If turns_left=2 and health 15, might take fatal to eat, but could survive without? If health 15 >2, can survive 2 turns. Better avoid fatal. We can condition fatal_penalty low only if health <= min(20, turns_left?) Actually if turns_left < health, no starvation before end; don't take fatal. If health <= turns_left, starvation before end if no food. So low fatal only if health <= max(5, turns_left?) Let's define `starving = my_health <= max(1, turns_left)`? If turns_left small, health 15 >2, not starving. Use fatal_penalty low if `my_health <= 20 and my_health <= turns_left + 5`? Simpler: low if health <=20 and turns_left > health? But if turns_left 500, yes. If turns_left 2, no. Implement:
```
desperate = my_health <= 25 and turns_left > my_health
fatal_penalty = 5_000_000 if not desperate else 1_000_000
```
If health 10, turns_left 500 -> desperate. If health 10, turns_left 5 -> not desperate (will survive to end), avoid fatal. Good. If health 10, turns_left 10 -> health <= turns_left, might starve exactly at end if no food; maybe desperate? If health==turns_left, after turns_left turns health 0 at end? Ranking at max_turns: if alive at turn limit? If health reaches 0 on turn max_turns, elimination maybe before end? If max_turns reached, maybe still? Safer eat. Use `turns_left >= my_health` desperate. So condition `my_health <= 25 and turns_left >= my_health`.

Food weight endgame: If turns_left small, increase food if not longest? But if turns_left < health, no need eat for survival, but need length. If not longest, increase. okay.

Now, adjust tail bonus if turns_left small: If turns_left < 20, survival to limit priority; tail bonus maybe high if health sufficient. But if not longest, food. Our tail_bonus currently 80k if turns_left<=30. Maybe keep. If turns_left < 10 and health>20, avoid risks, tail bonus 250k? Could set tail_bonus high if turns_left<15 and not desperate? But food weight endgame high. Hmm.

Simplify: `tail_bonus = 250_000 if (health > 45 or turns_left < 20) and not desperate else 80_000`. But if desperate, low. Let's code:
```
desperate = my_health <= 25 and turns_left >= my_health
tail_bonus = 80_000 if desperate else 250_000
if health <= 45 and not desperate and turns_left > 30: tail_bonus=120_000?```
Maybe too complex. Use earlier: `tail_bonus = 250_000 if health > 45 and turns_left > 30 else 80_000`. If turns_left small, tail_bonus 80k, food weight endgame high, may chase food. But if survival to limit, maybe should avoid. However if turns_left small, food weight high but fatal penalty high; nonfatal food maybe okay. Length matters. Fine.

Now, `i_am_longest = my_length >= max_enemy_len`. If no enemies, max_enemy_len=0, true. If multiple, if equal longest, true. Head-on equal fatal; we avoid.

Now, maybe if I am longest and turns_left small, can just survive; food weight not too high. Our fw increases if turns_left <40 regardless, may chase food. If longest, no need. Add condition: if i_am_longest and turns_left < 30, do not multiply endgame as much? Could set `if turns_left < 40 and not i_am_longest: fw*=2`; if longest, maybe *1. But eating increases length, still good but risk. Let's adjust:
```
if turns_left < 40:
   if not i_am_longest: fw *= 2
   else: fw = int(fw*1.2)
if turns_left < 15:
   if not i_am_longest: fw *= 2
```
Need integer. okay.

Now, trap penalty threshold: `min_space = max(4, min(80, my_length))`. If length huge 100, need space 80. If safe_space less, penalty. But in crowded board, may have no better. okay.

Now, maybe safe_space excluding threat_fatal could be too low if many enemies. If safe_space < min_space, penalty may make all moves bad; choose least. okay.

Now, consider if threat_fatal mask marks many cells around enemies; safe_space might undercount actual safe. But survival.

Now, let's think about possible hidden requirement: `decide(state)` may be called after game ended? Probably not. If state empty, fallback.

Now, let's consider code size. Need final answer only code block plus <=300 Chinese strategy. Code can be long but okay. Need ensure no syntax errors. We'll write carefully.

Potential improvements: Use `__name__`? not needed.

Now, let's simulate code in head for syntax.

```
import random
import time

DIR_ORDER = ...
...
GRID_W = 0
...

def ensure_grid(w,h):
    global GRID_W, GRID_H, CELLS, NEIGHBORS, DIR_NEXT, COORDS
    if GRID_W == w and GRID_H == h: return
    GRID_W=w; GRID_H=h; CELLS=w*h
    COORDS=[None]*CELLS
    DIR_NEXT=[None]*CELLS
    NEIGHBORS=[None]*CELLS
    for y in range(h):
      for x in range(w):
        i=y*w+x
        COORDS[i]=(x,y)
        nxt=[]
        neigh=[]
        for d in DIR_ORDER:
           dx,dy=DELTA[d]
           nx=x+dx; ny=y+dy
           if 0<=nx<w and 0<=ny<h: ni=ny*w+nx
           else: ni=-1
           nxt.append(ni)
           if ni!=-1: neigh.append(ni)
        DIR_NEXT[i]=nxt
        NEIGHBORS[i]=neigh
```
Direction order: up, down, left, right. DELTA values. Good.

`DIR_INDEX = {d:i...}`.

`direction_between(head, neck):`
```
def direction_between(head, neck):
    if head == neck: return None
    hx,hy = COORDS[head]
    nx,ny = COORDS[neck]
    dx=hx-nx; dy=hy-ny
    return DELTA_TO_DIR.get((dx,dy))
```
Need DELTA_TO_DIR global.

`body_to_idx(body, w, h):`
```
def body_to_idx(body, w, h):
    res=[]
    for p in body:
       x=p[0]; y=p[1]
       if 0<=x<w and 0<=y<h:
          res.append(y*w+x)
    return res
```
If p not indexable, exception caught.

Flood function. Use `INF = 9999` global.
```
def flood(start, occ, own_mask, threat, food_mask, target, deadline):
    visited = bytearray(CELLS)
    visited[start]=1
    current=[start]
    dist=0
    total=0; safe=0; min_food=INF; tail_found = (target != -1 and start == target)
    pt=time.process_time
    while current:
       if pt() > deadline: break
       nxt=[]
       for p in current:
          total += 1
          if (not threat[p]) or p == start: safe += 1
          if min_food == INF and food_mask[p]: min_food = dist
          if target != -1 and p == target: tail_found = True
          for nb in NEIGHBORS[p]:
             if not visited[nb] and not occ[nb] and not own_mask[nb]:
                visited[nb]=1
                nxt.append(nb)
       current=nxt
       dist += 1
    return total, safe, min_food, tail_found
```
Uses global CELLS, NEIGHBORS. Good. If start out of range? no.

Potential performance: `not occ[nb]` where occ is bytearray; okay. `not own_mask[nb]`.

Now, `quick_fallback(state)` maybe uses LAST_DIR. Need not ensure_grid? Could use width/height and simple deltas.
```
def fallback(state):
    try:
       w=int(state['width']); h=int(state['height'])
       you=state['you']
       head=None
       for s in state.get('snakes',[]):
          if s.get('id')==you:
             body=s.get('body')
             if body: head=body[0]
       if head is not None:
          hx,hy=head[0],head[1]
          # prefer LAST_DIR if inside
          if LAST_DIR in DELTA:
             dx,dy=DELTA[LAST_DIR]
             if 0<=hx+dx<w and 0<=hy+dy<h:
                return LAST_DIR
          # choose direction toward center or inside
          best=None; best_score=-10**9
          for d in DIR_ORDER:
             dx,dy=DELTA[d]; nx=hx+dx; ny=hy+dy
             if 0<=nx<w and 0<=ny<h:
                score = -abs(nx*2-(w-1))-abs(ny*2-(h-1)) + random.random()
                if score>best_score: best_score=score; best=d
          if best: return best
       if LAST_DIR in DIR_INDEX: return LAST_DIR
    except Exception:
       pass
    return LAST_DIR if LAST_DIR in DIR_INDEX else 'up'
```
But if LAST_DIR leads into wall, fallback center chooses. Good.

Main `decide`:
```
def decide(state):
    global LAST_DIR
    try:
        result = decide_main(state)
        if result not in DIR_INDEX:
            result = LAST_DIR if LAST_DIR in DIR_INDEX else 'up'
        LAST_DIR = result
        return result
    except Exception:
        result = fallback(state)
        if result not in DIR_INDEX: result='up'
        LAST_DIR = result
        return result
```
Need if decide_main returns None. okay.

Now, `decide_main` uses global LAST_DIR; if turn==1 set LAST_DIR=None. But if exception before? okay.

Let's write decide_main carefully.

```
def decide_main(state):
    global LAST_DIR
    turn = int(state.get('turn', 1))
    if turn <= 1:
        LAST_DIR = None
    w = int(state['width']); h=int(state['height'])
    ensure_grid(w,h)
    you = state['you']
    snakes = state.get('snakes', [])
    my = None
    for s in snakes:
        if s.get('id') == you:
            my = s; break
    if my is None:
        return fallback(state)
    raw_body = my.get('body', [])
    if not raw_body:
        return fallback(state)
    my_body = body_to_idx(raw_body, w, h)
    if not my_body:
        return fallback(state)
    my_length = int(my.get('length', len(my_body)))
    my_health = int(my.get('health', 100))
    max_turns = int(state.get('max_turns', 500))
    turns_left = max(0, max_turns - turn)
    # food mask
    food_mask = bytearray(CELLS)
    for p in state.get('food', []):
        try:
           x=p[0]; y=p[1]
           if 0<=x<w and 0<=y<h: food_mask[y*w+x]=1
        except Exception: pass
    my_head = my_body[0]
    current_dir = None
    if len(my_body) >= 2:
        current_dir = direction_between(my_body[0], my_body[1])
    if current_dir is None:
        current_dir = LAST_DIR
    opp_dir = OPP.get(current_dir) if current_dir else None
    candidate_dirs = [d for d in DIR_ORDER if d != opp_dir]
    if not candidate_dirs:
        candidate_dirs = DIR_ORDER[:]
    my_tail_stays = len(my_body) >= 2 and my_body[-1] == my_body[-2]
    # masks
    own_full = bytearray(CELLS)
    for p in my_body: own_full[p]=1
    own_move = bytearray(CELLS)
    for p in my_body[:-1]: own_move[p]=1
    own_space_normal = bytearray(CELLS)
    for p in my_body[:-2]: own_space_normal[p]=1
    own_space_stay = bytearray(CELLS)
    for p in my_body[:-1]: own_space_stay[p]=1
    # others
    occ_others=bytearray(CELLS)
    threat_fatal=bytearray(CELLS)
    threat_win=bytearray(CELLS)
    enemy_head_coords=[]
    max_enemy_len=0
    for s in snakes:
       if s.get('id') == you: continue
       raw = s.get('body', [])
       if not raw: continue
       body = body_to_idx(raw, w, h)
       if not body: continue
       length = int(s.get('length', len(body)))
       if length > max_enemy_len: max_enemy_len = length
       head = body[0]
       enemy_head_coords.append(COORDS[head])
       tail_stays = len(body) >= 2 and body[-1] == body[-2]
       mark = body if tail_stays else body[:-1]
       for p in mark: occ_others[p]=1
       edir = None
       if len(body) >= 2:
           edir = direction_between(body[0], body[1])
       eopp = OPP.get(edir) if edir else None
       emark = set(mark)
       for di, dname in enumerate(DIR_ORDER):
           if eopp is not None and dname == eopp:
               continue
           ni = DIR_NEXT[head][di]
           if ni == -1: continue
           if ni in emark: continue
           if length >= my_length:
               threat_fatal[ni] = 1
           else:
               threat_win[ni] = 1
    deadline = time.process_time() + (0.8 if turn <= 1 else 0.04)
    best_dir = None
    best_score = -10**30
    desperate = (my_health <= 25 and turns_left >= my_health)
    fatal_penalty = 1_000_000 if desperate else 5_000_000
    tail_bonus = 80_000 if desperate else 250_000
    if my_health <= 45 and not desperate and turns_left > 30:
        tail_bonus = 150_000
    i_am_longest = my_length >= max_enemy_len
    # Food weight
    fw = 1200
    if my_health < 60: fw *= 2
    if my_health < 35: fw *= 2
    if turns_left < 40:
       if i_am_longest: fw = int(fw * 1.2)
       else: fw *= 2
    if turns_left < 15 and not i_am_longest:
       fw *= 2
    if desperate: fw *= 2
    min_space_threshold = max(4, min(80, my_length))
    for d in candidate_dirs:
       di = DIR_INDEX[d]
       ni = DIR_NEXT[my_head][di]
       if ni == -1: continue
       eating = bool(food_mask[ni])
       imm_mask = own_full if (eating or my_tail_stays) else own_move
       if occ_others[ni] or imm_mask[ni]:
           continue
       if time.process_time() > deadline:
           # if time low, choose this safe direction if no best? maybe break
           if best_dir is None:
               best_dir = d
           break
       if eating:
          space_mask = own_full
          target = -1
       elif my_tail_stays:
          space_mask = own_space_stay
          target = -1
       else:
          space_mask = own_space_normal
          target = my_body[-2] if len(my_body) >= 2 else -1
       total_space, safe_space, food_dist, tail_found = flood(ni, occ_others, space_mask, threat_fatal, food_mask, target, deadline)
       fatal = bool(threat_fatal[ni])
       win = bool(threat_win[ni])
       hx, hy = COORDS[ni]
       min_enemy = 99
       for ex, ey in enemy_head_coords:
          md = abs(hx-ex)+abs(hy-ey)
          if md < min_enemy: min_enemy = md
       center = abs(hx*2 - (w-1)) + abs(hy*2 - (h-1))
       score = 0.0
       if fatal: score -= fatal_penalty
       if win: score += 20_000 if i_am_longest else 5_000
       if tail_found: score += tail_bonus
       if safe_space < min_space_threshold:
           score -= 400_000
       score += safe_space * 80 + total_space * 10
       food_eff = food_dist if food_dist < INF else 200
       score -= food_eff * fw
       score += min_enemy * (30 if my_health > 50 else 10)
       score -= center * 5
       score += random.random()
       if score > best_score:
           best_score = score; best_dir = d
    if best_dir is not None:
       return best_dir
    # fallback no immediate safe
    # quick evaluate candidate_dirs, if none all dirs
    dirs_to_try = candidate_dirs if candidate_dirs else DIR_ORDER
    best = None; best_val = -10**9
    for d in dirs_to_try:
       di = DIR_INDEX[d]
       ni = DIR_NEXT[my_head][di] if my_head < CELLS else -1
       val = random.random()
       if ni != -1:
          val += 10
          if not occ_others[ni]: val += 5
          if not own_full[ni]: val += 3
          if not threat_fatal[ni]: val += 2
          # prefer toward center/food? maybe
          hx,hy=COORDS[ni]
          val -= (abs(hx*2-(w-1))+abs(hy*2-(h-1))) * 0.01
       if val > best_val:
          best_val=val; best=d
    if best is not None:
       return best
    if current_dir in DIR_INDEX:
       return current_dir
    return LAST_DIR if LAST_DIR in DIR_INDEX else 'up'
```
Need `INF` global. `food_dist < INF`: flood returns INF=9999 if none. Good.

Potential issue: If time low and best_dir None, we set best_dir=d and break, but d may be first safe without scoring. okay. But if best_dir already exists, break leaves best. Good.

Potential issue: `desperate = my_health <=25 and turns_left >= my_health`. If turns_left 0, health 0? If my_health 0? decide called if alive? health maybe >0. If turns_left 0, desperate false unless health 0. okay.

Potential issue: If `my_tail_stays` true, immediate mask own_full. But if my_body has duplicates and own_full marks spawn; candidate new head not. okay. Space mask own_space_stay old_body[:-1] may mark old head and body. For initial [s,s,s], own_space_stay marks s,s (set s). BFS from adjacent blocks spawn. okay.

Potential issue: For other snakes, possible heads `emark = set(mark)`. If tail unique, mark excludes tail, so enemy can move into its tail. Good. If tail duplicate, mark includes tail cell. Good. But if enemy body length 3 stacked, mark all body (tail_stays true) set spawn. possible heads adjacent not spawn. Good.

Potential issue: `direction_between` uses COORDS; ensure_grid called. Good.

Potential issue: If body has head and neck not adjacent due corrupted state, direction_between returns None; possible heads all. okay.

Potential issue: If enemy length field less than len(body)? Use length for head-on. If length smaller due duplicates? official length maybe. okay.

Potential issue: If my_length from state maybe not equal len(my_body). For own masks use body length. For head-on use my_length. If my_length differs, tail target maybe. okay.

Potential issue: If food_mask start cell true and candidate eating, immediate safe. BFS food_dist=0. Score high. Good.

Potential issue: In fallback quick evaluate, `own_full[ni]` marks own body; but if ni is own tail unique and tail moves, own_full still marks, penalizes but all fatal. okay.

Now, let's think about if `decide_main` calls `fallback(state)` when my not found; fallback may use LAST_DIR. But if state invalid, okay. However fallback uses `LAST_DIR in DIR_INDEX` but LAST_DIR global might be None. okay.

Now, possible hidden judge: `random` module seeded per game, but if we import random and use random.random, okay. If random not initialized? It says initialized. If not, still works.

Now, can we make code more aggressive/strong? Maybe add "prefer moves that reduce distance to nearest food" more. Our food_weight base 1200, safe_space weight 80. A difference of 10 food steps =12k, space difference 150 cells=12k. Balanced. Tail bonus dominates. Good.

Maybe tail_bonus 250k too high, causing excessive tail-chasing. Could lower to 150k. Let's tune: safe_space max ~900*80=72k, total ~9k, food dist max 200*1200=240k. Tail 250k. If a move tail_reachable but food far, vs non-tail food close: tail wins unless food weight high. In normal health, survival first. Good. If no tail_reachable moves, chooses max space/food. If tail_reachable but leads to small space (trap penalty 400k), may avoid. Good.

Could set tail_bonus 180k. Maybe. But unknown. Let's keep 250k.

Now, potential issue: `safe_space` excludes threat_fatal cells, but threat_fatal may include many cells adjacent to equal/longer enemies. In brawl, safe_space could be tiny everywhere, trap penalty applies to all. Then food/space decide. okay.

Now, think about if enemy is shorter but possible head cell marked threat_win, safe_space counts it safe (not fatal). Good. If enemy length < mine but could eat food this turn and become equal? If it moves into our new head which is food, both eat, still shorter. If it eats another food before head-on impossible same turn. okay.

Now, let's consider if our length is 3 initial, enemy length 3, threat_fatal around enemy. If we are equal, avoid head-on. Good.

Now, potential issue with simultaneous food: If two snakes heads move to same food, both eat. If we are shorter and enemy also, we die if same cell? Actually both eat then elimination: longest survives. If shorter, die. threat_fatal if enemy length >= mine. If enemy length > mine, fatal. If enemy length == mine, fatal. If enemy length < mine, win. Good.

Now, possible nuance: If multiple heads same cell, longest survives; if one snake also collided with body? If our head enters food cell that is also enemy's current tail moving? If enemy tail unique moves out, no body. If enemy tail stays, occ_others blocks. Good.

Now, let's think about pathing through enemy possible heads in BFS. We count safe_space excluding fatal cells but still traverse through them? In flood, neighbor check does not block threat, so safe_space may count safe cells beyond fatal cells, even though path passes through fatal. The safe count counts cells not threat, but connectivity through threat may overestimate safe space. Example a corridor behind an enemy adjacent cell; safe_space counts beyond because BFS traverses threat cell. We wanted maybe safe connectivity. Could adjust: In BFS, for safe count, we could not traverse threat cells except start? But we also need total. Could run two BFS or modify: If threat cell encountered, we could still traverse for total but not count beyond as safe? Hard. Current safe_space overestimates. But fatal candidate penalty only for start. Maybe okay. Could instead use `total_space` for score and penalize threat count? We don't count threat count. Maybe safe_space overoptimistic. But threat cells are only adjacent to enemy heads; beyond them may be actually unsafe because enemy can move next turn. Overestimating may lead into contested areas. Could improve by blocking threat_fatal in BFS neighbor expansion, but then total/space conservative. Let's consider changing flood to optionally block threat for expansion. If we block threat, space may be very small near enemies, but survival. Could be too conservative but maybe good. We can block threat_fatal except allow start. In neighbor check: `if not visited[nb] and not occ[nb] and not own_mask[nb] and not (threat[nb] and nb != start):`. Then BFS only explores through non-fatal cells. This makes safe_space = reachable area avoiding cells enemy can contest this turn. But threat is current possible heads; after one turn, threat changes. Blocking may avoid moving into areas near enemies. In brawl, many threat cells, could cause bot to see no space and make weird moves. But maybe survival. We can compromise: Don't block threat for expansion, but subtract number of threat cells? Could count `threat_count` and score penalty. Let's add count of threat cells visited: In flood, `danger_count += 1 if threat[p] and p!=start`. Score penalty `danger_count * 200`. Then safe_space = total - danger_count. But connectivity through danger still. Maybe okay.

Could run BFS with threat blocked only if not desperate? Time okay. Let's modify flood to accept `block_threat` boolean. But calling two BFS? Maybe one with block_threat=True for space/food/tail. If start threat, allow start but not expand into threat? If start threat, candidate fatal penalty huge anyway. Blocking threat could make food unreachable if path crosses threat; good avoid contested food. I think conservative is better for survival. Let's set neighbor check to block threat_fatal cells (except start). Then total_space and safe_space? If threat blocked, total_space is safe area. We can still count safe as total. But if start threat, only start reachable maybe. That's okay. Need tail_reachable through threat false. This may be too restrictive but avoids head-on zones. Let's evaluate: Enemy possible heads are only 3-4 cells around each head. Blocking them creates small obstacles. Not too bad. In brawl 11 snakes, block up to 44 cells. Okay. It may fragment but reasonable. Let's implement blocking threat in BFS. Then safe_space = total_space (since threat not visited except start). But we can keep safe count. In flood neighbor check:
```
if not visited[nb] and not occ[nb] and not own_mask[nb]:
    if threat[nb] and nb != start: 
        pass
    else: add
```
But if threat cell is target tail? Should tail reachable through threat? If tail cell threat, maybe dangerous; block. If start threat, we allow start but no expansion to threat neighbors? Actually if start threat, neighbor threat block? It will block all threat neighbors, but non-threat expand. Good.
Then in loop, safe count maybe total. We can simplify but keep.

Food distance will avoid paths through fatal threat. Good. If no safe food, may starve; desperate mode could reduce fatal penalty but BFS still blocks threat for candidate scoring. If desperate and only food behind threat, candidate fatal start maybe? If path through threat but start not threat, BFS won't find food, food_eff=200; may choose other. But if all food behind threat, maybe starve. Could in desperate mode not block threat. Add parameter `block_threat = not desperate`. If desperate, allow traversing threat (but still penalize start fatal). Good. Modify flood signature `block_threat`.

Implement flood:
```
def flood(start, occ, own_mask, threat, food_mask, target, deadline, block_threat=True):
 ...
 for nb in NEIGHBORS[p]:
   if visited[nb] or occ[nb] or own_mask[nb]: continue
   if block_threat and threat[nb] and nb != start: continue
   visited[nb]=1; nxt.append(nb)
```
Counting safe: if threat[p] and p!=start, danger; but if block_threat, none beyond start. safe = total - (1 if start threat else 0). We can still use `safe` count as cells not threat. Good.

In decide, call `flood(..., block_threat=not desperate)`. If desperate, BFS may traverse threat, safe_space counts non-threat but total includes. Score uses safe_space; if safe_space low but total high? We use safe_space. Maybe in desperate use `space_metric = max(safe_space, total_space//2)`? To allow risky paths. Add:
```
space_metric = safe_space if not desperate else max(safe_space, total_space // 2)
```
Use in score and trap. Good.

Modify flood returns total, safe. In desperate, safe may be low. Use space_metric.

Now, if threat blocking in normal, tail_reachable requires path not through threat. Good.

Now, update scoring: `space_metric = safe_space if not desperate else max(safe_space, total_space//2)`. Trap threshold uses space_metric. Score += space_metric*80 + total_space*5 maybe. Good.

Now, threat_fatal start: If fatal, score penalty. BFS may start threat; if block_threat, expands to non-threat neighbors? In flood, start added even if threat. In neighbor check, `nb != start` only for nb, so from start threat can expand to non-threat. Good. It can survive one step? If start is possible enemy head, enemy may move there and kill; fatal penalty. If not killed, subsequent area. okay.

Now, desperate false normal blocks threat. Good.

Potential issue: threat_fatal includes cells enemy can move into, but if enemy is blocked by our body after our move? We compute before our move. If our new head occupies a cell, enemy moving there head-on; threat valid. For other cells in BFS, threat from current enemy heads maybe not valid after we move? Approx. okay.

Now, maybe we should also block threat_win? If enemy shorter, head-on we win, so not fatal; could traverse. Good.

Now, adjust `safe_space` in flood if threat blocking: In loop, `if (not threat[p]) or p == start: safe += 1`. If start threat, safe doesn't count start? Actually condition p==start counts start safe. Good. If block threat, no other threat. safe=total. Good.

Now, food_dist in desperate with threat traversed: If food reachable only through threat, found. Good.

Now, scoring in desperate: fatal penalty lower, food weight high. Good.

Now, potential bug: If `block_threat` true and target tail is threat, BFS won't enter target, tail_found false. okay.

Now, let's think about if all safe candidates have BFS space 0 due threat blocking? start always count 1. Trap penalty if threshold >1. All penalized. Choose based. okay.

Now, maybe threat_fatal should not block cells that are food? If enemy and I both can move to food, head-on fatal. Avoid. If desperate, allow. okay.

Now, let's adjust code for flood and scoring accordingly.

Now, consider if we should include possible enemy heads from enemies that are longer/equal but may die due colliding with our body? For threat cell, if enemy moves into our new head, head-on. If enemy's path to that cell is our new head; no body. If cell is adjacent to enemy head and also adjacent to my new head? It is my new head. okay.

Now, maybe enemy possible heads should consider that if enemy moves into a cell occupied by my old body (which will remain), it would die and cannot contest my new head unless my new head same cell. Since my new head safe not in old body. Threat cells elsewhere not relevant? For BFS blocking, threat cells include enemy possible heads even if occupied by my old body? emark excludes enemy own body only, not occ_others. Some threat cells may be inside my old body; BFS blocked by own_space anyway. okay.

Now, possible optimization: For enemy possible heads, if cell is in occ_others (other bodies) and not my new head? Could still be blocked. For threat blocking, marking them may over-block. But conservative.

Now, let's think about if we should account for walls in head-on risk: enemy possible heads only inside. Good.

Now, maybe use `length = int(s.get('length') or len(body))`; if length missing. Use try.

Now, test fallback if `state` lacks width? Exception caught returns 'up'. okay.

Now, final strategy summary <=300 Chinese characters. Need after code block. Should describe: one-step safety, flood fill, tail reachability, head-on risk, food urgency. Keep <=300 chars. We'll produce Chinese.

Before final, let's review code for syntax and possible NameError.

Globals:
```
INF = 9999
DELTA_TO_DIR = {v:k for k,v in DELTA.items()}  # but DELTA values tuples, okay.
```
Need define after DELTA.

In ensure_grid, use DELTA. Good.

In fallback, uses `random` and `LAST_DIR`. If random not imported? imported.

In decide_main, uses `fallback` which may use LAST_DIR. If my not found, return fallback. But fallback might return direction not in candidate? okay.

Potential issue: In decide_main, after `if turn <= 1: LAST_DIR = None`, if fallback called, LAST_DIR None. okay.

Potential issue: `my_body[:-2]` when my_body length 0? we check. length min 3. okay.

Potential issue: `own_space_normal` for length 3 marks my_body[0:1], okay. For length 2, empty. For length 1, empty.

Potential issue: target tail `my_body[-2]` when len>=2. If not eating and not tail_stays. If length 2, target body[-2]=head? But moving? Snake length min 3. okay.

Potential issue: If `my_tail_stays` true due duplicate but we are not eating, immediate mask own_full. But own_full includes head; candidate new head cannot be head. Good. If candidate new head is old tail duplicate cell, own_full blocks. Good.

Potential issue: If my_tail_stays true and candidate eats, immediate mask own_full, space own_full. okay.

Potential issue: In BFS, if `own_mask` is own_full and start is food (eating), start not in own_full because new cell not old body; safe. If food on old body, immediate unsafe.

Potential issue: occ_others building: For each enemy, mark body if tail_stays else body[:-1]. If enemy body length 1, body[:-1]=[], but snakes length >=3. okay. If tail unique, tail cell passable. Good.

Potential issue: Enemy possible heads uses `emark = set(mark)`. If mark large, set. If enemy current_dir unknown and head==neck, eopp None, all dirs. If head != neck but body duplicate? direction between head and neck distinct. okay.

Potential issue: `DIR_NEXT[head]` exists. head idx valid. Good.

Potential issue: If `threat_fatal[ni]` set by enemy possible head but ni is also occupied by occ_others? immediate unsafe if occ_others; candidate skipped. Good.

Potential issue: In candidate loop, if time.process_time() > deadline and best_dir None, set best_dir=d and break. But we didn't check if d safe? We are inside after immediate safe. okay. If best_dir exists, break. Good. But if time low after evaluating some, returns best. okay.

Potential issue: `deadline = time.process_time() + (0.8 if turn <= 1 else 0.04)`. CPU limit turn1 1s, later 50ms. 0.04 leaves 10ms margin. Precompute ensure_grid before deadline; turn1 precompute within 0.8? ensure_grid maybe before deadline? In code, ensure_grid called before deadline. Turn1 load limit 1s; ensure_grid trivial. For later, ensure_grid already done. Parsing before deadline could take time not accounted? We set deadline after parsing others. Actually in pseudo deadline after building masks. That uses CPU before deadline; if parsing slow, could exceed. Should set deadline at start of decide_main after turn check: `deadline = time.process_time() + (0.8 if turn<=1 else 0.04)`. Then use throughout. Let's move deadline near top after ensure_grid? But ensure_grid needed. Set after turn reset: `start_time = time.process_time(); deadline = start_time + (0.8 if turn <=1 else 0.045)`. Use 0.045 maybe. But if ensure_grid and parsing exceed, still. But small. Set early.

In candidate loop, check deadline. In flood, deadline. Good.

Maybe use 0.042 for later. 50ms limit, need margin. Use 0.04. Turn1 0.85. okay.

Potential issue: If turn==1 and ensure_grid plus BFS within 0.85, okay.

Potential issue: If state max_turns missing, default 500. okay.

Now, let's consider if our program may exceed CPU due random.random in loops? small.

Now, maybe use `int(fw * 1.2)` etc. fw int. okay.

Now, let's write final code cleanly.

Double-check `direction_between`: If COORDS not initialized? ensure_grid called before. In fallback, direction_between not used. okay.

Now, possible hidden judge: The module may be loaded and `decide` called without random imported? We import. okay.

Now, let's think about if `print` discarded; no prints.

Now, potential strategic weakness: Our bot may be too defensive, losing length competition. But in battle, survival often key. In single duel, if both survive to 500, length wins. Our bot may tail-chase and not eat enough. We increased food weight endgame and if not longest. In duel, if opponent baseline eats, we need eat. Health decreases; if we avoid food due tail bonus, health lowers, desperate/food weight increases, then eat. Should get food. But maybe health 45 threshold; at health 45, tail_bonus 150k, fw=2400 (health<60), food dist difference 50=120k, still tail. At health 35, fw=4800, tail_bonus 150k? my_health <=45 -> tail_bonus 150k if not desperate and turns_left >30. Food diff 30=144k, can override. So by health ~35, chase. That means may go 65 turns without food if tail safe. Health 100, okay. But in duel, opponent may outgrow. If we are shorter, fw*1.5, tail maybe 150k, health<60 fw 3600, diff 50=180k, chase earlier. Good.

Could lower tail_bonus to 120k normal to eat more. Let's adjust maybe: tail_bonus desperate 60k, normal 180k. Space max ~80k, food normal max 240k. Tail still strong but not overwhelming. Let's set:
```
tail_bonus = 60_000 if desperate else 180_000
if my_health <= 45 and not desperate and turns_left > 30: tail_bonus = 100_000
```
Trap penalty 350k. This may balance. But tail survival important. Maybe 180k okay.

Food weight base 1500? If base 1500, normal food dist 50=75k. Tail 180k. Health<60 3000 ->150k. Good. Let's set base 1500. Then desperate high. Space weight 80. okay.

Tune scoring:
```
fw=1500
if health<60: fw*=2
if health<35: fw*=2
...
score += space_metric*80 + total_space*5
```
Food unreachable penalty 200*fw; normal 300k, can dominate tail. If no reachable food, all penalized; space decides. okay.

Trap penalty 350k. If safe_space small, avoid. Good.

Now, fatal_penalty 5M normal. If fatal move food close, not chosen unless desperate. desperate fw maybe 1500*4*2=12000, food_eff 0, fatal -1M, safe no food -200*12000=-2.4M, so fatal chosen. Good.

Now, implement final weights:
- fatal_penalty = 1_000_000 if desperate else 5_000_000
- tail_bonus = 60_000 if desperate else 180_000; if health<=45 and not desperate and turns_left>30: 100_000
- trap_penalty = 350_000 if space_metric < threshold
- space_metric*80 + total*5
- fw=1500, multipliers.

Now, maybe if turns_left < 40 and i_am_longest, we shouldn't increase fw much. Code: if turns_left<40: if not i_am_longest fw*=2 else fw=int(fw*1.1). if turns_left<15 and not i_am_longest fw*=2. Good.

Now, if desperate, fw*=2.

Now, min_enemy weight: If health>50, 30 else 10. If min_enemy 99 no enemies -> 2970, small. okay.

Center weight 5. center max ~ (30+30)*2? For 31, center score max 60? Actually abs(2x -30) max 30, sum 60, weight 5 =300. small.

Win head bonus 20k if longest else 5k. Could encourage head-on with shorter. If fatal penalty absent. okay.

Now, maybe if `win` and `fatal` both true (multiple enemies), fatal penalty dominates. Good.

Now, fallback no safe: We might return a direction that is opposite current_dir? candidate_dirs excludes, but if no candidate_dirs? dirs_to_try candidate_dirs. okay. If current_dir None, all.

Now, let's consider if our snake is length 3 stacked and my_tail_stays true; immediate safe candidates all adjacent. BFS space_mask own_space_stay marks spawn. If threat blocking, maybe space. Good.

Now, potential issue: In initial stacked, my_tail_stays true, so immediate mask own_full. But own_full marks spawn. Candidate moving to adjacent safe. If adjacent cell is food, eating true, space own_full. If not, space own_space_stay. okay.

Now, let's think about if body length after eating: The state length field may be larger than len(body) due overlapping? Example length 4 body 4. okay. If body duplicates, len(body)=length. Good.

Now, one more strategic idea: In single duel, if I am longer than opponent and near end, I can seek head-on? Our win bonus small. Could maybe actively intercept shorter opponent by moving into threat_win cells. But not necessary.

Now, possible issue: Our BFS blocks threat_fatal, but threat_fatal is based on enemy possible moves this turn. For space after my move, enemies will have moved, so threat cells this turn may be empty next turn. Blocking them may underestimate space. But survival. Maybe use threat blocking only for food path, not space? Hmm. If too conservative, bot may avoid open areas near enemies. In brawl, enemies everywhere; might get stuck. But if threat cells are only adjacent, not huge. okay.

Now, let's consider if enemy is longer and adjacent behind us. Threat_fatal includes cells around enemy, including maybe our only escape? If our move into a threat cell, fatal penalty. If all moves fatal, desperate? not if health high; fatal penalty high but all candidates fatal, choose best. It may choose a fatal move because no alternative. If there is a nonfatal move into wall? immediate unsafe, not considered. If all immediate safe moves fatal, best fatal. okay.

Now, if an enemy longer is adjacent, often moving away not fatal. Good.

Now, maybe need to consider "possible head" of enemy if enemy current direction reverse excluded. If enemy body collapsed, all. If enemy just ate and tail stays, direction still from head/neck. okay.

Now, let's think about if enemy current_dir derived from body but body last two overlap, head/neck distinct. Good.

Now, possible issue with coordinate system: y from top to bottom, up y-1. DELTA correct. ensure_grid neighbors: up ny=y-1. Good.

Now, let's ensure final code block only. The user requested reply only one python code block, then <=300 words strategy. We can include code block and summary. Ensure no extra text before. Good.

Now, let's mentally run code for syntax with global variables in functions.

In ensure_grid, assigning to global CELLS etc. Need declare global. Good.

In flood, uses global CELLS, NEIGHBORS, INF. It takes deadline, block_threat. Need define signature with block_threat=True.

In decide_main, call `flood(ni, occ_others, space_mask, threat_fatal, food_mask, target, deadline, not desperate)`. Good.

In flood, `process_time = time.process_time` local. But if deadline passed, okay.

Potential micro-optimization: In flood, `if min_food == INF and food_mask[p]: min_food = dist`. If food found at level, still continues; okay.

Potential bug: If target tail is blocked by own_mask but target == start? no. If target not visited, tail_found false. Good.

Potential bug: If BFS start is blocked by threat and block_threat true, we still add start. Neighbor check blocks threat nb, but if start threat and neighbor non-threat, expand. Good.

Potential bug: If start is threat and block_threat true, safe count counts start safe due p==start. space_metric at least 1. Good.

Potential bug: In candidate loop, if time.process_time() > deadline and best_dir is None, set best_dir = d and break. But we haven't scored d; maybe d safe but could be bad. Better than none. If best_dir exists, break. okay.

Potential bug: If no safe candidates, fallback uses `my_head < CELLS` always true. okay.

Potential bug: In fallback quick evaluate, `own_full` and `occ_others` may not be defined if no safe? They are defined before candidate loop. yes.

Potential bug: If exception occurs before occ_others defined, decide_main raises and wrapper fallback uses state only. okay.

Now, let's consider if state includes dead snakes? It says alive only. okay.

Now, maybe need to handle `state['you']` as string? Compare with s.get('id') maybe int. If string, maybe. Use `if s.get('id') == you`. okay.

Now, possible hidden judge: `state` values may be tuples, dict. okay.

Now, let's think about if `random.random()` in fallback before random seeded? okay.

Now, could there be recursion? no.

Now, code length maybe ~350 lines? okay. Need final answer not too huge but fine.

Let's maybe further improve by adding "if only one enemy and both lengths, avoid being closer than 2"? Not needed.

Now, let's think about possible bug in own_space_normal: For not eating, not tail_stays, future own block should be old_body[1:-1]? Wait earlier we derived own_space_mask = new_body[1:-1] = old_body[:-2]. But this blocks old head through third-last. Does it block old neck? For old [h,n,t], old[:-2]=[h], blocks h but not n (new tail). Good. For old [h,a,b,t], old[:-2]=[h,a], blocks h,a, not b (new tail). Correct. It does not block new head. Good. So own_space_normal correct. But what about old body cell `old_body[-3]`? It becomes middle? Example old [h,a,b,t], new [new,h,a,b]. new_body[1:-1]=[new? wait new_body[1:-1] = [h,a] yes. Blocks h,a. b tail passable. Good.

If current tail_stays and no eat, actual new body maybe [new,h,a,b,b] or [new,h,a,b]? We use own_space_stay old_body[:-1]=[h,a,b], blocks b. Conservative. Good.

If eating, own_space full old_body [h,a,b,t], new body [new,h,a,b,t], tail t stays next turn? If ate this turn, tail will not move next turn, so block all old_body. Good.

Now, immediate own_move for not eating not tail_stays: old_body[:-1] blocks h,a,b (all except old tail). New head cannot move into b (second-last) but can into t (old tail). Correct. If old tail duplicate? tail_stays true, use full. Good.

Now, occ_others for future space uses mark = body if tail_stays else body[:-1]. For other snake not tail_stays, excludes old tail. But after this turn, their new tail is old_body[-2], which will move next turn? For space next turn, should exclude old_body[-2]? occ_others excludes only old tail, includes old_body[-2]. Conservative by one segment. Could overblock. But okay. Could use body[:-2] for others future space? But immediate collision this turn: their old_body[-2] remains occupied after their move, so if we are considering our move this turn, new head cannot go there. For future BFS after our move, at next turn their old_body[-2] may be tail and move, so could be passable. Our occ_others includes it, conservative. If we wanted more accurate, for space we could use `occ_others_space` with body[:-2] for non-tail-stays. But immediate check needs body[:-1]. Could build two occ masks: occ_others_immediate and occ_others_space. This could increase space and food reachability. Let's consider.

For other snakes, after they move this turn (simultaneously), occupied cells = body if tail_stays else body[:-1]. At the end of turn, their new tail is old_body[-2] if not tail_stays. Next turn, if they don't eat, that tail will move. For our BFS for future space (starting next turn), we could exclude their new tail (old_body[-2]) if it is unique and they are not currently eating? But we don't know if they will eat this turn. Approx. Classic pathfinding often treats moving tails as passable. Excluding old_body[-2] might be optimistic but good. However if old_body[-2] duplicate, still blocked via old_body[-3]. We can create `occ_others_space` mark = body if tail_stays else body[:-2]? But if body length 3 [h,n,t], body[:-2]=[h], excludes n (new tail) and t. After their move, new body [new,h,n], tail n will move next turn, so n passable. h occupied by neck, block. Good. This opens more. For immediate safety, use occ_others_immediate body[:-1]. For BFS, use occ_others_space. This may improve pathing. Need also threat possible heads based on immediate? okay.

Let's implement two occ masks: `occ_others_imm` and `occ_others_space`. For each enemy:
- imm_mark = body if tail_stays else body[:-1]
- space_mark = body if tail_stays else body[:-2] (but if duplicate tail? body[:-2] may still include duplicate cell if len>2? Example body [h,n,t,t] tail_stays true -> body all. Initial [s,s,s] tail_stays true -> all. If non-tail-stays but body has duplicate not at tail? possible? body[:-2] handles duplicates in remaining.)
Use occ_others_imm for immediate candidate check and enemy possible? Enemy possible own mark should use imm_mark (their own body collision this turn). Use occ_others_space for BFS. This gives more space. Need fallback quick uses occ_others_imm maybe. Let's adjust.

Build:
```
occ_others = bytearray(CELLS)  # immediate
occ_others_space = bytearray(CELLS)
...
mark_imm = body if tail_stays else body[:-1]
mark_space = body if tail_stays else body[:-2]
for p in mark_imm: occ_others[p]=1
for p in mark_space: occ_others_space[p]=1
```
But for enemy possible heads, use `emark = set(mark_imm)`.
BFS flood uses occ_others_space. However, if an enemy tail is unique and we can follow it this turn, immediate occ excludes old tail; space also excludes old tail and new tail? body[:-2] excludes old tail and new tail. Good.

But need ensure immediate candidate check: `if occ_others[ni] or imm_mask[ni]`. Good.

For fallback quick, use occ_others.

This may make BFS less conservative, but more accurate. Threat blocking still.

Now, for other snakes current head: space_mark body[:-2] excludes old head? For body [h,n,t], body[:-2]=[h], includes head. Good. For length 2, body[:-2]=[], but min 3. For length 3, includes head. After their move, old head occupied by neck, block. Good. For length 4 [h,a,b,t], body[:-2]=[h,a], blocks old head and a; new tail b passable. Correct.

If tail_stays true, space_mark body all, conservative.

Let's adjust code accordingly. Need flood call `occ_others_space`.

Potential issue: If enemy just ate (tail_stays), body all includes duplicate tail. After their move this turn, tail stays, but if they don't eat, next turn tail might move? State tail_stays means tail stays this turn. For future BFS after this turn, if they don't eat, tail may move next turn but duplicate may resolve. We block all conservative. okay.

Now, update candidate immediate safe uses occ_others (imm). Good.

Now, possible head threat: If enemy possible head cell is their own tail unique, emark excludes, threat marked. Good.

Now, own space masks similar: own_space_normal old_body[:-2] (analogous). Good.

Now, adjust fallback quick if no safe: use occ_others immediate. okay.

Now, code update.

Let's think about if using occ_others_space in BFS can consider cells that will be occupied by enemy new heads unknown. We don't know; threat mask covers adjacent possible heads. Good.

Now, maybe for BFS we should also not block enemy current heads? occ_others_space includes current head, because old head remains occupied by neck after move. At next turn, enemy head has moved elsewhere, but neck moved to old head? Wait after enemy moves, old head becomes occupied by neck. At the start of next turn, that cell is body (neck), not head. It remains obstacle unless it is tail? So block. Good.

Now, potential issue: In BFS from my new head, my own old head is blocked by own_space_normal. At next turn, old head becomes neck/middle, obstacle. Good.

Now, let's consider if we can move into a cell currently occupied by enemy tail unique; immediate safe, BFS space_mark excludes old tail and new tail, so cell passable. Good.

Now, update code variables: In decide_main, rename `occ_others` immediate, `occ_others_space`. In candidate loop immediate check uses `occ_others`. BFS uses `occ_others_space`. Fallback uses `occ_others`.

Now, enemy possible heads uses `emark = set(mark_imm)`. Good.

Now, maybe threat_fatal cells that are in occ_others_space but not immediate? If enemy possible head is a tail cell passable, threat. Good.

Now, let's review final code with these changes.

Potential issue: In fallback quick evaluate, `own_full` marks all own body, but if ni is own tail unique, moving into tail immediate safe (if not tail_stays). own_full penalizes. But fallback only when no safe, okay.

Now, let's think about if we should include `state['turn']` maybe 0? It says from 1. If turn<=1 reset. okay.

Now, one more advanced feature: If there are no enemies (shouldn't, but maybe after all die? game ends if 0/1 snakes, decide maybe not called). If no enemies, max_enemy_len=0, i_am_longest true, enemy_head_coords empty, min_enemy=99. threat masks empty. Bot will chase food/space. Good.

Now, possible issue: If food_mask has no food? Rules always snakes+1, but if state missing. BFS food_dist INF, food_eff 200. okay.

Now, let's think about if `my_health` could be 0? If alive, health >0 maybe. If 0, desperate true if turns_left>=0, fatal penalty low. okay.

Now, let's simulate code for a simple state to catch NameError:
- ensure_grid uses `CELLS` global, initially 0. Good.
- direction_between uses COORDS; if head/neck invalid index? body_to_idx valid. Good.
- In decide_main, after ensure_grid, `CELLS` set. Bytearray(CELLS). Good.

Now, final code should not use type hints requiring imports? Can use but not needed. Avoid annotations for compatibility? Python 3.13 okay, but keep simple.

Now, let's consider if process_time deadline in flood with `block_threat` false in desperate. If desperate, threat_fatal start penalty lower, BFS traverses threat. Good.

Now, maybe in desperate, trap threshold should use total_space not space_metric? We use max(safe,total//2). Good.

Now, potential bug: In flood, if `block_threat` false, threat cells visited; safe count excludes them. space_metric in desperate max(safe,total//2). If path mostly threat, total high but safe low; space_metric half total. okay.

Now, scoring with `food_eff = food_dist if food_dist < INF else 200`. If food_dist INF but desperate, penalty 200*fw huge; all candidates no food penalized equally. If one candidate food reachable through threat due block_threat false, food_dist finite, chosen. Good.

Now, if normal block_threat true, food behind threat not reachable; may choose no food. If health lowers desperate, then can. Good.

Now, possible issue: In normal, tail_found may be false if tail path crosses threat. Good avoid.

Now, let's think about if threat_fatal mask should be used in immediate candidate safety as hard exclude? We use score penalty. If nonfatal alternatives, fatal penalty huge, so excluded. If all fatal, choose. Good.

Now, maybe if fatal candidate also has `occ_others_space` BFS blocked threat and safe_space 1, trap penalty; still if all fatal choose least. okay.

Now, consider if a candidate is immediate safe but `threat_fatal[ni]` true because enemy possible head. If enemy is actually not able to move there due our body? The cell is our new head; enemy moving there head-on. It is able if adjacent and not own body. Good.

Now, possible bug: Enemy possible heads exclude reverse based on derived direction. But if enemy body collapsed, all. If enemy current direction unknown but LAST_DIR for enemy not known. Could under/over estimate. okay.

Now, let's consider if we should derive enemy direction from previous state global? Could track all snakes previous bodies to infer direction when collapsed? Not worth.

Now, final strategy summary in Chinese <=300 characters. Let's draft:
"采用单步安全+洪泛评估。先用对手下一回合仍占用的身体（会动的尾巴除外）排除必死格；把相邻且长度不短于我的敌头可能撞到的格子列为致命风险。候选方向做 BFS：计算可活动空间、能否绕回自己尾巴、到最近食物距离。按饥饿/残局加权，优先无致命碰撞、保持尾部可达和足够空间，危急时抢食物。"
Count maybe 150 chars. Good.

Now, ensure final answer code block only then summary. The user requested code block after maybe. We'll provide.

Let's now write final code in final. But before final, maybe we can run through code one more time for syntax. I'll compose code carefully.

Full code:
```
import random
import time

DIR_ORDER = ['up','down','left','right']
DELTA = {...}
OPP = {...}
DIR_INDEX = {...}
DELTA_TO_DIR = {...}
INF = 9999

GRID_W=0...
LAST_DIR=None

def ensure_grid(w,h): ...
def direction_between(head,neck): ...
def body_to_idx(body,w,h): ...
def flood(...): ...
def fallback(state): ...
def decide_main(state): ...
def decide(state): ...
```

Check `DELTA_TO_DIR = {v: k for k, v in DELTA.items()}` values tuples hashable. Good.

In ensure_grid, use `nonlocal`? no global.

In decide_main, if my is None return fallback(state). But fallback may return direction not updating LAST_DIR? Wrapper updates. okay.

In fallback, if head is list [x,y], okay. If LAST_DIR leads inside but maybe into body; fallback only for exceptions, okay.

In fallback, uses `random.random()`; if random throws? no.

In decide wrapper, if result not in DIR_INDEX, use LAST_DIR. But if LAST_DIR None, 'up'. Then LAST_DIR=result. Good.

Now, possible issue: In decide_main, if turn==1 resets LAST_DIR, but if fallback called within decide_main and returns, wrapper sets LAST_DIR to fallback. okay.

Now, let's inspect decide_main variable `deadline`. Set after turn reset and ensure_grid? I'll set:
```
start_cpu = time.process_time()
deadline = start_cpu + (0.85 if turn <= 1 else 0.040)
```
But ensure_grid after? If ensure_grid after deadline, precompute time counted against but deadline maybe too soon. Set after ensure_grid? Turn1 precompute small. But to be safe, set after ensure_grid. However parsing before deadline? We can set at very top after turn reset, then ensure_grid; if ensure_grid takes 5ms, okay. Later ensure_grid returns quick. Use 0.042 later? Let's use 0.040. If parsing takes 10ms, candidate time less. But okay. Maybe set deadline after building masks? Then BFS could exceed. Better set early. Use 0.045 for later? Limit 50ms, leave 5ms. 0.045 okay. Turn1 0.85. Let's set `deadline = time.process_time() + (0.85 if turn <= 1 else 0.045)`. If CPU time measured, 45ms. Good.

But if first turn ensure_grid + parsing within 0.85, okay.

Now, in candidate loop, if time.process_time() > deadline, break. If best_dir None, set to d. But if d safe and we break, okay.

Now, in flood, deadline check per level. If time exceeds, returns partial counts. Could make score based on partial, but rare.

Now, in fallback quick evaluate, if `my_head` maybe not defined? It's in decide_main after my_body. If no safe, defined. okay.

Now, maybe in decide_main, after building masks, if no candidate_dirs? candidate_dirs always at least 3 if current_dir, or 4. If current_dir invalid string? OPP.get returns None, candidate_dirs all. Good.

Now, one subtle bug: `current_dir = LAST_DIR` if derived None. If LAST_DIR is opposite of actual because previous move was invalid? We try not invalid. But if body collapsed and LAST_DIR set, okay. If LAST_DIR None, all. Good.

Now, maybe if my snake just ate and body last two overlap, `my_tail_stays` true. But if it also is initial stacked, my_tail_stays true. Good.

Now, let's consider if own_space_stay mask old_body[:-1] for initial [s,s,s] marks s (because duplicates). BFS from adjacent blocks spawn. But after moving out, spawn still occupied by two segments, so block. Good.

Now, let's think about if enemy possible heads uses `emark = set(mark_imm)`, but mark_imm list may have duplicates; set okay. If enemy length long, set membership O(1). Good.

Now, code for body_to_idx: If body point invalid, skip. This could make body shorter and tail duplicate inference off. But state valid. okay.

Now, final code. Ensure no line too long? okay.

Let's also consider if `state` is not dict but mapping? uses get. okay.

Now, maybe hidden judge uses PyPy? time.process_time available. okay.

Now, final answer. But before final, maybe think if there is a simpler stronger algorithm like Hamiltonian that we missed. Our heuristic likely decent. Need deliver final. Ensure summary <=300 Chinese chars.

Let's produce final code.