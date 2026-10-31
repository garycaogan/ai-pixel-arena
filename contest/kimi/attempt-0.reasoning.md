We need craft strongest bot. Need deeply reason mechanics and opponents. Need output code block then <=300 Chinese chars strategy. Need ensure valid standard lib, timing robust. We can write sophisticated.

We need infer exact simultaneous moves. Need decide.

Goal survival then length. Board 15x15 duel, 31x31 11. Foods count maintained # alive +1, random empty likely. Opponents strong, varied.

Need robust flood fill / game tree / adversarial.

We have state no prior enemy direction? We can track bodies and infer. First body 3 stacked. Need turn moves. Tail mechanics exact:
- move each head chosen; tail simultaneously retract one
- hunger
- eat if head on food, length +1 tail appended (next turn tail not move)
- collision: head into any body except heads, including own. Wording tail has retracted step1, can follow others tails; but just eaten tail does not move.
Elimination simultaneous.
- Head-head same cell longest survives others; ties all die. Head on existing body.
- dead snakes disappear.
Head crossing paths without same destination no issue. Heads can move into former body tail? tails removed.
We can estimate opponent choices and safety.

Need produce in one response. Need code robust unknown corner cases. Global info reset process. We can track last state.

We need account invalid reversal: choice into neck ignored and original direction. For our decide perhaps return. For enemies, simulate invalid reversal according prior direction. Opponent code may return invalid; exact original direction. We can maintain per id dir. In stacked early, direction inference from body. body[0] to body[1] same, no direction from state. We can use last state movements.

Could run forward search with survival evaluation. Need fit 50ms. Python 31x31 11 snakes, lengths maybe. Need efficient sets/bitsets.

Simplest robust:
- immediate candidate legal wall/self survival
- evaluate via flood fill plus food distance + health + enemy threats.
- Beam/minimax lookahead maybe.

Could simulate one-step all enemy likely moves. Evaluate head-on risks.
- Food pursuit safe using BFS path and survival simulation with space.
- Voronoi.

Could implement iterative deepening game tree in limited states? Multiple simultaneous. Need 50ms. At duel could perform deeper own and enemy. Brawl broad.

We need maximize rankings. Strong snake bot likely use flood fill, A*, enemy prediction, aggression/head collision, length.

Let's formulate.

At each decide:
Parse widthheight, alive ids, own.
Maintain previous bodies to infer directions.

Movement invalid:
Our returned direction if neck distinct and opposite current; referee changes to current. We'll choose legal.

At start directions inferred? First turns from previous head positions. For each enemy, prior state and current body:
new head = prev body[0] + direction, unless weird. body prior list. infer diff current head-prev head. If no movement? Always. At state turn 1, set default maybe based spawn pattern? We have current bodies and food only. Initial body all three same. Each chooses direction turn1. Need predict defaults impossible. Candidate all.

For subsequent enemy current direction infer current head - prev head. Store. If snake ate and body? Head diff still.

After our decide, global cache overwritten next call before previous action. To update our direction, store choice at end.

Need understand body representation for length and overlap. It always includes length elements, possible duplicate tail after eating. Start three duplicates. Movement implementation:
Given old body, move head. tail popped, except if last two duplicates? "new section added at tail, so next turn tail does not move." Their movement says each head move, tail simultaneously retract. Then eating after, append. So at move before eating, tail always popped. If tail duplicates from last food, pop one duplicate but coordinate stays same -> tail visually does not move. Good. We can simulate candidates by old list [newhead]+old[:-1], then if food append old[-1]? Let's see standard:
Old body [H,...,T-1,T]. Move+tail retract -> [NH,H,...,T-1] length same. If food: health and grow: new segment added at tail [NH,H,...T-1,T]. So yes append old tail if ate. If duplicate at old tail from prior food, move pops one duplicate -> tail coord remains.

Enemy candidates move sets similar.

Safety after one simultaneous move:
For each possible own move and presumed enemy move:
- own destination outside / own body after tail pop collision. Important body collision evaluated after movement; opponents bodies updated. Own intermediate updated.
- head-head.
Could evaluate worst-case if enemy all candidates impossible exponentially. Opponent behavior prediction. Maybe use per-snake candidate set and risk scoring. For duel exact minimax possible over joint 4x4. For 11 use heuristic.

Opponent model:
- baseline avoids immediate death, sees space, nearest food. Strong opponents unknown.
- use candidate values based on safety, fooddistance, aggression.
Could select top 2/3 per opponent.

Could do own candidate evaluation using rollout/planning.

Survival is paramount. Flood fill in one move can avoid traps. Space requirement based length and health, but region can be traversed repeatedly if snake's tail opens. Static flood fill over current occupied (non-tail) is conservative. Need Voronoi or reachable region. On 31 board, enough space. Duel 15, traps significant.

We can compute exact self survival horizon via game state search assuming no enemies: candidate route and flood fill. Or route to food and tail-chase.

Potential approach:
1. Compute immediate move outcomes against enemy predicted choices.
2. For each own candidate, perform depth-limited adversarial search for duel (minimax simultaneous), and stochastic/best response? Brawl evaluate joint predicted top moves.
3. Heuristic state scoring includes:
   - death huge
   - reachable free space flood fill
   - food reachable before starvation
   - enemy distance and head-head danger
   - territory Voronoi
   - length and health
   - aggression if longer can kill.
4. Search rollouts where enemies use heuristic, own maybe evaluate.

Could implement depth maybe 6-10 duel, 4 brawl. Need timing.

Represent grid occupancy bitboards as Python int (961 bits) efficient. Snake body tuple. Food set.
For simulation exact requires body tuple lists. Branching:
Duel joint top own 4 x enemy 4 up to 16, depth 6 -> 16M too high. Alpha-beta with move ordering maybe. Or evaluate candidates using rollouts enemy deterministic. Could run iterative minimax with only enemy top 2 => 4*2^depth maybe 4k.

Brawl 10 enemies deterministic heuristic, branch own 4 depth 5 ~1k. Good.

But heuristic each step occupancy expensive if all snakes. Optimize.

Could instead select own candidate and simulate several random/plausible opponent policies for 5 steps, using flood fill. Time.

Important no hard time call duration visible. `time.process_time()` standard library. Use deadline ~0.043 sec leaving buffer. First turn 1 sec but later 50 ms. Loading <=1 sec. Global precompute okay.

Potential exact safety:
Given own new body and positions of enemies, calculate available squares reachable before collision with static bodies? `flood_count` occupancy. But moving enemy tails open. Conservative.

Need avoid starvation. Foods plentiful. BFS from head to nearest foods through cells not permanently occupied. Enemy bodies obstacles. Since tails open, only exclude non-tail body segments. Need route safe accounting dynamic. We can path next move maybe.

Evaluate current resulting state:
- space flood from own head through passable current cells excluding bodies (except maybe own tail); cap e.g. 80/160.
- food distance BFS up to health*? Exclude body cells except tail.
- if no food within health, death inevitable absent enemy? Actually cannot eat outside BFS. severe.
- region capacity relative length. Because snake can move in region if enough. Flood count less length means trap (unless own body vacates; excluding own non-head body but can enter tail as opens, static might undercount). Better flood with own body all blocked is too conservative. Exclude own tail one square. Others eventually vacate if moving. Could flood with occupancy excluding all own body? That can route through neck incorrectly. Use hazards body except last k maybe. Common flood fill remove own body but it can overestimate and choose loops? For area measure, area from head with walls and other snakes; own body should obstacles except tail. Use tails maybe two? Tail opens sequentially, so exclude tail maybe duplicate. Enemy tail excluded. Foods as open.
- "room" number squares.
- if room < length, trap risk.
- path to food.

Voronoi: BFS multi-source from all snake heads through passable current occupancy (heads excluded), count cells closer to own vs enemies, with distances. Food control. But enemy heads moving dynamic. Could help brawl. Maybe too expensive per branch.

Head-on:
If our head destination also enemy's candidate, if own length > enemy we win; equal die; shorter die. Can aggressively kill if longer. If own length less, avoid unless enemy chooses elsewhere.
Head-to-body kill can be induced by entering enemy neck? If head lands where enemy body after movement, only if body remains. Since enemy moves too. Can't force unless predict.
Can block opponent paths.

Potential coordinate zones/center.

Need robust scoring of dead snakes based resulting rank? Decisions don't know final. Length secondary. Survival huge.

Implement policy.

Let's design bot in detail.

Data structures:
DIRS list ordered maybe ["up","right","down","left"], vectors.
OPP = {"up":"down",...}
norm cell tuple/list -> (x,y).

Globals:
LAST = None maybe state data.
DIRECTIONS = {}
OUR_LAST_DIR = None
OUR_LAST_BODY? For infer current own dir can just state body if distinct, else OUR_LAST_DIR. But if returned invalid and forced, our action actual might differ. We know choose valid.
History maybe track enemy behavior? Not needed.
At start update direction:
for each snake:
 prev_body from PREV_BODIES
 if prev and prev[0]:
   dx = head-prev head
   if dx in dirs, dir = that.
   else keep.
Store current bodies.
If dead remove.

We need predict enemies and simulate.

Build board `cell_id = y*w+x`, bit ops. Occupancy bit of all body cells maybe duplicates no issue.
For each candidate snake movement:
`move_body(body, d, ate)`:
newh.
base = (newh,) + body[:-1]
if ate: base + (body[-1],)
Need collision after move uses all bodies postmove. Foods at new head. All snakes move.
An enemy candidate may reverse; if direction equals body[1] and distinct, action invalid and actual old direction. Important `effective_dir(snake, d)`: if len body >1 and body[1] != body[0] and d == opposite(current_dir inferred), then d=current. For initial body duplicates no neck, so all moves valid? "掉头（走回自己脖子那一格）无效"; neck coordinate same as head due stacked. Any move isn't "走回" maybe all valid. On turn 2 body maybe [new, spawn, spawn], still neck coordinate spawn not equal head, reverse to spawn valid (this is stacked body but then collision? head enters own body after tail retraction? Old [n,s,s], new reverse [s,n,s] because pop one s; head s collides own tail s => dies? reverse into neck and collision likely. It is valid? "neck" coordinate spawn; yes reverse; then after tail pop one duplicate still tail there and collision => death. In real initial stacked movement tricky. Could simply avoid reverse based coordinates. Prediction candidate immediate death will filter.

For enemies with unknown dir, candidate all with immediate non-suicide perhaps.

Predicted action scoring:
Given state object, for each enemy candidate evaluate immediate outcome. Need joint interactions. For own evaluation, perhaps enumerate own move and choose top enemy action independently.

Could define `heuristic_move_score(snake, d, ctx)`:
- simulate enemy alone tail pop; wall/self immediate -> -inf
- candidate head occupancy current updated enemy body? Other current bodies, with their tails may vacate. For enemy deciding simultaneous unknown.
- Avoid cells that are current body segments except moving tail and food.
- Food reward.
- Flood space.
- distance to nearest food.
- avoid possible head-on if our length >=.
- avoid adjacent to longer enemy heads.
- random tie by `random`.
But generating top candidate each branch expensive.

Alternative for each turn precompute enemy top 2 moves once based current. Then own candidate and joint outcomes. During rollout, recompute deterministic actions.

Need potentially run MCTS-like own simulation.

Let's specify a lightweight simulator state:
class SimState maybe tuples:
- turn irrelevant
- snakes tuple of `(id, body tuple, health, length, dir)` including own. length len body likely.
- foods frozenset.
No food spawn? To simulate future, after eaten, referee adds random food to keep count. Unknown random but deterministic module seed can use; however random calls affect future actual? Allowed and initialized. We can call random but impacts only our process maybe judge same process? decide in same process, random use perhaps influences food spawn? Judge seeds module before game, if we consume random, likely yes because judge uses random module? It may use same random; user can direct use. But predictions need spawn rules. Could copy state random? no. Better don't consume? Evaluation food spawn matters less; can use fixed food respawn maybe at far/free cell deterministic. But in sim exact future unknown. Since module random seeded, calls in bot could alter actual referee if same global, but no issue maybe unfair? Don't.
Use foods minus eaten plus deterministic generated open cell (center/random hash), or no respawn. Foods plentiful. For route evaluation, current foods suffice. In actual future respawn. Could use pseudorandom deterministic based turn/id without random. Fine.
But 50ms.

Alternatively no full simulation and focus direct.

Let's first build robust decision selection with immediate joint:
Generate all own valid moves that don't hit wall/self after tail.
For each own candidate:
- own destination.
- Consider enemy top candidate sets. Determine joint safety:
  - update enemy bodies for each chosen candidate.
  - collision own head with enemy postmove body (excluding head)
  - head collisions if equal dest: compare lengths.
  - death.
Score average/min across joint top options.
For 10 enemies joint combinations impossible. Assume enemies move predicted best, plus assess individual risks:
  - Enemy head danger set: for each enemy candidate cells with probability/weight. If own dest:
    - if candidate may choose, compare length and score.
  - enemy post bodies; exact tail.
Could evaluate top action vector and a small random sample combinations for top 2, capped e.g. 24. In duel all combos.
Could optimize enemy selection top2.

Enemy candidate generation:
For each enemy:
 all four dirs effective. Basic illegal wall/self after tail.
 Score via `enemy_policy`. Pick best 1 or 2; include maybe unknown turn all.
 Need account food. Use BFS distance to food from new head.
 
Own candidate evaluation after joint:
- exact result.
- flood.
- food BFS.
- next-turn safety (mobility) critical: simulate one more step perhaps.
- search rollout.

Could use expectiminimax with enemy heuristic selected actions.

Simplify recursive search:
At each SimState, decide own move among immediate safe candidates under predicted enemy moves. For each own candidate, enemy moves deterministic via policy (not adversarial joint), simulate exact. Evaluate after depth. This might ignore traps. For duel, include enemy top moves and minimax:
`search(state, depth, alpha,beta)` returns own utility.
At node:
- own moves up to 4
- enemy moves top 2/3
- for each own move, utility min over enemy moves of recurse.
But if own move immediate depends on enemy. 8 combos depth.
Depth dynamic based time:
 duel depth 7 maybe 8^7 2M; with top enemy 2, 8^? own 4*2=8, 2m too much. alpha/pruning but utilities.
Could depth 5 ~32k, each simulation and eval too high. Optimize and deadline iterative.

For brawl deterministic all enemies; own branching 4 depth 5=1024, manageable. But generating policy for 10 at each depth huge. Cache action plans per snake body/foods maybe.

Could implement fixed depth rollout not full recursion: for each initial move, simulate deterministic own greedy choices subsequently. Less useful.

A one-step "area" heuristic likely enough, but "strongest" should improve.

Let's create `evaluate_state` robust and search with iterative.

Represent occupancy dynamically:
`all_occupancy(snakes)`.

Simulate joint selected moves:
Input dict id->dir.
- Determine ate based current food at dest before removal.
- For each alive snake, effective move, new body.
- Need collisions and starvation:
   all heads.
   Health each -1, if <=0 die.
   body_bits after all moves.
   For each snake head:
      if outside die.
      if head cell bit in union of body segments excluding each snake's own head. This includes other heads. Head-head handled separately.
      Duplicate head cells group; longest survives, ties all die. Wording collision body includes other head? "head collides with any snake body (except snake head)" so heads not body. Then head-head separate.
      If own head at another's body dies; enemy likewise.
      If head same as own tail after movement due food duplicate? Own body collision excludes head only. possible.
- Dead removed.
- Food: remove eaten cells, then add `alive_count+1 - len(foods)` deterministic empty cells. Original may spawn multiple? "被吃掉的食物在随机空格重新出现", exactly one per eaten; invariant yes. We can replenish.
Need choose deterministic cell not on bodies. `open_cells` scan perhaps 961* branch expensive. Precompute maybe scan from hash. In search, can skip respawn and keep foods; but resulting food count decreases, okay short horizon. Yet eating reward evaluated immediate. Better no respawn for speed. Current foods sufficient. Or replenish deterministic from precomputed center order with bit. Could.
At actual one-step only no respawn matters next decisions. Search short.

Scoring terminal:
If own dead: -1e9 plus turn depth maybe.
If all enemies dead: +1e8.
Length as reward small.
Survival utility shaped.

Heuristic evaluate from perspective own:
- Base survival 0.
- length * maybe 30.
- health * 0.1.
- space metric.
- nearest food.
- food count owned / Voronoi.
- threats.

Need avoid choosing low space even if food.
Flood fill:
Given resulting state, passable = all cells minus body occupancy. But heads occupy. For own region from head, cannot enter any body (including head irrelevant). BFS into open cells, count up to cap.
Enemy and own tails may open. Exclude tails from obstacle: all last segments maybe. But if just ate, tail doesn't move; represented duplicate tail, popping still duplicate means blocked next step. Need identify mobile tail:
At current state, on next move each tail segment always pops one representation; if last two same coordinate, remains blocked. To determine cells becoming open next step: body[-1] coordinate always popped, but if body[-2]==body[-1], coordinate remains in body. So simply remove all last body cells from occupancy, duplicates no impact if duplicate.
Flood obstacles body bits minus tails of all snakes. Also enemy heads block. This predicts next passable.
`region_count(state, sid, cap)`.
Count and frontier/openness. BFS.
If count < own length maybe deadly. But snake can travel along own tail, count excluding tail adds one only, still maybe low. Use thresholds.

Food distances:
Multi-source BFS from own head through passable (bodies minus all tails), until food. Need path length. If none within health, penalty.
At state after movement, health already decremented. If distance >= health? Move takes distance turns; health after d moves is h-d, eat at turn d when head arrives after hunger, so requires health-d >? hunger then health maybe h-d, then eat. If h-d <=0 dies before eat. So dist < health (if h=1 adjacent food, after move h=0 then dies at hunger before eating, impossible! Rule hunger before food; need health after decrement >0, so dist <= health-1).
If no reachable within health-1, likely starvation unless respawn. penalty huge.

Space and route to food should pass current enemy tails. For future dynamic enemy, unknown.

Voronoi:
Multi-source BFS all heads through passable current occupancy. But heads sources, body obstacles. Number cells closer own. Could assess food control. In brawl 31x31 961 BFS potentially okay once per candidate? 4* maybe. Too much. Evaluate each branch potentially. Could only base candidate one step and cap.
Maybe compute region own only enough.

Risk:
Enemy heads adjacent can move into our head next turn. Since our current head and enemy heads:
For each enemy:
- enemy length vs own.
- Manhattan dist. If 1, next turn potential head collision at own current head if both remain? Enemy moves into own head while own also moves away normally; head collision only simultaneous destination, enemy enters vacated own head no issue. If our next destination same one of enemy's next cells. Danger sets.
- Adjacent enemy can body-block etc.
Score avoid proximity to longer/equal enemies, but if longer can seek.

Aggression:
In duel, if own longer, head-on is winning. Strong strategy chase enemy head or cut off. Add score based distance to enemy head:
- If own length > enemy: closer is positive, but risk body.
- If <=: distance positive safety.
In brawl, head-on kills based longest among entrants; longer than particular enemy doesn't guarantee if third longer. Avoid multi.
Could target shorter enemies near wall/trap.
Food is plentiful; length determines ties and head duels. Eating useful.

Enemy policy:
Need infer "medium baseline". Avoid immediate death, space, nearest food. We can emulate. Strong bots maybe similarly. Enemy best moves.
`policy_candidates(state, sid, topn)`:
for dirs:
- effective.
- Simulate just snake alone? Need current occupied dynamic. A direction's post body and immediate collision potential:
  - dest outside invalid.
  - Determine current other body cells that will still be occupied. For each other, remove its tail (unless duplicate). If dest in those body segments (excluding heads? If another head current, it moves so vacates; if candidate head same as another current head? occupied head moves, so no body collision; head-head only if dest is another destination, not current head. Current heads all vacate, so allow).
  - Own same body after tail pop.
- food distance BFS from dest maybe approximate Manhattan nearest food, with wall not issue.
- region maybe local.
- prefer center/food.
- avoid head-to-head potential: for each other snake, if their candidate destinations include dest and length >= sid length, penalty; but circular. Just adjacent enemy heads longer.
- return top 1/2.
At each recursive node, this approximates rational.

However for search, perhaps policies should account food path. `nearest_manhattan` enough, board no obstacles mostly. Space maybe flood count capped 40 each action costly. For brawl 10*4 each recursive -> too high. Cache policy result by state? state changes every node. But maybe compute only:
- immediate candidate valid
- food bonus
- min manhattan food
- center
No flood in recursive policy. At root more detailed tie.

Could use a "planning fallback" if search times out: root candidate score.

Time management:
`START = process_time()`, deadline maybe 0.042 after first? Since loading separate. First turn can use 0.7 sec. Need know state["turn"]==1 => 0.85 maybe. Else 0.041. Python overhead in decide measured, return before. We can make time checks in recursion every 256 nodes. If timeout exception internally and use best found.
Potential judge's CPU slower. Use 0.038 sec. First 0.80 sec perhaps.
No exception externally.

Iterative search:
At root generate own actions and enemy candidate sets.
For duel:
 - depth 1, then 3,5? search simultaneous depth includes rounds.
 - For brawl 2,3 maybe.
Need always have root evaluation.

Search function with alpha-beta:
State includes `snakes`, foods. Own id.
At node if own absent terminal.
`own_actions` = dirs sorted by root? Generate all effective not wall/self-alone.
For each enemy, `policy_candidates` top N. In duel top maybe 3, brawl one? For joint cartesian in brawl no.
- duel: for each own action, min across each enemy action (top 3). If either action leads one/both death, recurse/evaluate. This is adversarial and robust. Branch up to 12, depth 5 ~250k; alpha-beta maybe.
- brawl: choose each enemy's single best policy independently, then evaluate own 4 moves; depth 3 ~64 nodes, each simulate 11 snakes. Could add perturbation: enemy best moves fixed.
Could make root candidate robustness individual danger rather than branch.
At brawl depth 4 depending time.
Potential ties and ordering.

Alpha-beta simultaneous min:
```
value(state, depth, alpha,beta):
 if terminal/depth0 eval
 if duel:
   best=-inf
   for oa:
      worst=inf
      for ea:
         v=value(sim, depth-1, alpha,beta?) 
         worst=min
         if worst <= alpha: break
      best=max(best,worst)
      alpha=max
   return
 else:
   enemy moves dict fixed
   max over own
```
At deeper brawl enemies deterministic.
Need pass alpha/beta perhaps. Terminal death values with depth to prefer later: own death `-1e7 - depth?` At root depth remaining; if die later, remaining lower, so utility `-1e7 - depth` means less depth => less negative? e.g immediate at d=5 remaining after sim 4 -> -1e7-4, later d=0 -> -1e7, immediate worse more negative. Good. Win +1e7+depth perhaps sooner larger.

Evaluation needs efficient. At depth 0, compute:
- region count maybe cap.
- nearest food BFS.
This can be expensive but nodes limited. Cache eval by state key? State tuples huge. Could use lru? dictionary global per turn cleared? Search call count. Use dict keyed `(snakes, foods)` memory; probably okay but building key itself. Python tuple hash. Could cache.

Move generation:
Basic action candidates should include reversal? Effective may be same current. Return own valid actual. For enemy, all action names but effective maps duplicates; if candidate reverse invalid equals current direction. To avoid duplicate, set of effective dirs. In policy.
At initial unknown dir, all distinct.
For own, choose effective direct and avoid invalid reversal. Since our dir tracked.

Body state as tuple of tuples.
Length can derive. Health.
Food tuple sorted maybe.

`next_state(state, moves)`:
- snakes list.
- For each id, action effective based dir stored in tuple.
- New body before eating? Movement and tail first. Determine ate from dest in foods. New body.
- health-1; if eat reset 100 and append tail.
- Check wall.
- body segment occupancy excluding head after all updates.
Could collision include dead snake bodies before removal? Elimination simultaneous; all moved; even snake starving dies, its body maybe obstacle for collision? "dead immediately disappear" simultaneous elimination. Wording elimination simultaneous: all criteria likely bodies of snakes that die still? "死掉的蛇立刻消失." If a snake starves same round, could its body be collision obstacle? Need infer. They say simultaneous判定; likely collisions evaluated on postmove state before removal, then all dead removed. A snake that head out has body remains within board until disappears; other head may hit it. We could approximate all moved body as obstacles regardless death. Then head-head. But dead snake disappears "立刻"; order criteria simultaneous means perhaps not obstacle. Baseline likely not rely.
We'll include bodies of all moved snakes for collision, then remove dead.
Head-head only among snakes not already body/wall/starve? "淘汰（同时判定）" likely all; if collide body and head same, death anyway.
For head-head same dest, longest among all whose heads there survives; if those had body collision maybe survival irrelevant except own head also in body. Fine.
Length = len(body).
- A snake may dest food, eat, then die due collision. It grew body before elimination.
- Food consumed by all simultaneous heads, then deaths. Remove if any ate regardless.
- Dead disappear.

Collision obstacle bit: each new body positions from index 1 onward. Note if another head at a position equal to own body? handled head-head not body because excludes heads; head cells of other snakes excluded automatically because obstacle excludes index 0. Own head excluded own.
For own body list can contain duplicate coordinates; bit.

Wall check.

Health: starts <=100. food map.

Deterministic policies:
`enemy_actions(st, topn)` returns list of dirs per enemy.
Need account current direction stored in tuple. If reverse action effective same current, dedup.
Basic passable at destination:
- dest wall false.
- simulate own body after move and see if dest in own body index1 => self collision (but other dynamic).
- other current bodies: after each moves, their tail pops. For static candidate check if dest in body[:-1]? Current head moves out, so exclude index0 and last. This approximates. If enemy ate? unknown. Use `body[1:-1]`.
- allow current head positions.
Score:
  - +80 if food
  - - nearest Manhattan to food * maybe 3, if no food.
  - health urgency if health<25.
  - space proxy count legal adjacent from dest under current occupancy (not full flood)
  - center preference slight.
  - danger: if any longer/equal snake head Manhattan 1? Candidate destination could be selected as head target. For each other whose head can move to dest and length>=, -60. If other shorter +20 aggression.
  - if sid is own? Policy maybe used baseline only enemies.
Pick topn with deterministic slight hash, no random to reproducibility. `random` allowed, but deterministic better.
Could emulate baseline's "space" with flood maybe for root enemy top2. But no.

Own action root scoring:
Search evaluate.

Evaluation detailed:
```
if own absent death
if no enemies win
score = length*120 + health*0.5
region = flood_count cap maybe max(80, length*3, 120)
score += min(region, cap)*4
if region < length: -5000*(...)
elif region < 2length: -500*(...)
fdist = food_distance(cap health-1)
if none: -10000 - ...; elif dist: -dist*(20 if hungry else 6)
foods accessible count within maybe 10 +.
mobility number of next own safe moves
threats:
 for enemy:
   d=manhattan heads
   if own len> enemy len+? score += (8-d)*15 in duel, maybe only if <=4
   else score -= max(0, 8-d)*(10/5)
 enemy region? maybe.
food target path safety.
center bonus slight in brawl? center has more options but more snakes. Position to open area.
```
Need ensure length not overpower survival. Region trap penalties.

Flood count passable:
- obstacle all body bits except tail coord of each snake. If duplicate tail, remains via bit from body[:-1], so okay.
- Start head is obstacle but BFS neighbors.
- Food accessible.
Potential own region can pass through current head of enemy? It moves next, but body collision dynamics. Excluding enemy head from obstacle could overestimate; include enemy head? At current postmove, enemy will move next, head vacates. Static region one-turn should allow tail but heads maybe hazard. Conservative include all enemy full body including head? BFS next move can't enter current enemy head because enemy moves away, but could head-head if chooses stay impossible. It can move into a square adjacent. We can exclude enemy head as vacating. Standard flood fill uses all snake bodies except tails. Keep heads as obstacle may underestimate. Include head perhaps safety.

We can compute both region conservative. Use all bodies except tails (enemy heads blocked). This is safe enough but might think trapped in tight interaction.

`flood_info` combined BFS returns count and first food dist. Use queue lists. Grid max961. cap maybe 100. If stop cap before finding food? Need continue if not found. Do one BFS to health max <=99. Food distance. Count first cap but continue.
Could return count capped 160, distance.

Need account health: food BFS obstacle. If distance >= health, penalty.

Space requirement: length can exceed board eventually (225/961) but max rounds and food. Duel could 100+. cap dynamic `min(w*h, max(80, length*3))` count. If region count exactly 225.

Evaluation region score saturates at `safe_need = length*3` maybe. `space_score=min(count, max(40,len*3))*3`.
If count < len: huge. But circular path with region count can equal length and survive by tail following. A snake filling region in a loop can survive indefinitely but no food unless food in loop. Penalize but not impossible.
Food distance independent.

Tail chase: If no food, score should follow tail? nearest food always.

Potential future food spawn could rescue. But survival priority.

Move risk head-on:
Search exact if enemy candidate set includes aggressive moves. Enemy policy may not choose head-on into longer own due penalty. If own shorter and enemy longer, enemy policy may choose aggressive. Need candidate top3 includes it. If all top moves avoid? Add explicit danger evaluation at root:
For each own candidate, for each enemy valid candidate:
- if destination equal and enemy length >= own => mark risk. Even if not policy top, avoid if another comparable safe action exists. Score penalty depending enemy length and number.
- if own dest in enemy post body for candidate => risk.
- enemy head candidate into our destination.
Could prune any move with possible immediate death under a plausible enemy action, unless all moves risky. Strong robust strategy. This is key.
`action_risks(root, ownmove)`:
for each enemy:
  for each enemy effective candidate not self/wall:
    if e_dest == own_dest:
      if e_len >= own_len => risk += large (tie death; if e shorter, own survives maybe enemy dies; but third)
      elif own longer => reward kill potential.
    Need enemy body after move: if own dest in e_newbody[1:] => risk. But collision with body can occur regardless enemy other death.
Also if multiple enemy heads same destination and own longest? Longest survives; if tie max all die. Determine group potential. For robustness, any equal/longer dangerous.
A "plausible" action could be intentionally suicidal by enemy; adversary may choose to kill us even if it dies (if equal) for ranking? Yes avoid.
Set candidate danger score.
Do not completely exclude if safe alternatives. Root base score - 20000*risk count, or only choose min risk.

Similarly own move may kill shorter by head-on if enemy predicted. Reward.

Enemy bodies dynamic: If dest is enemy current tail and tail pops, safe unless duplicate tail; our `newbody[1:]` exact for candidate action and food status. Good.
If enemy head goes same food, both eat.

Multi-enemy combinations:
For root, evaluate fixed predicted vector and danger independent.

Could calculate minimal maximum threat rank choose candidate with:
- number possible lethal enemy actions
- worst-case our length comparison
- expected.

For duel minimax exact top candidates handles.

Own action candidate generation basic:
All directions effective. If reversal invalid maps current, okay. Check dest wall.
Check self collision after own tail pop; if dest in new own body[1:] -> action always death, unless maybe food? still death, exclude.
Could enter another current tail; risky dependent.

Search state uses all four own possible even if immediate collision with predicted enemy, simulator handles death and minimax.

Enemy candidate topn:
At root duel 3 or all 4? Opponent strong adversarial, include all plausibly non-suicidal. Branch 4*4. Depth iterative until deadline.
At deeper maybe 2.

We can implement `search` duel with `topn=3 at depth >=?`. Generate enemy candidates each node expensive. At each state, for own 4, enemy 3. Use alpha beta.

Time benchmarks rough Python:
next_state duel: tuples, collision bits. 12 branches.
policy generation each node enemy maybe 4 with simple scores. Search depth 4: 12^4=20k * next state ~ maybe 0.1s. Alpha pruning and deadline. Use depth 3 likely. First turn can deeper.
Could transposition cache by state and depth. State tuple includes healths and foods, unique little repeat. no.

Move ordering:
Own candidate sort by static eval one-step; enemy sort by policy descending. Alpha-beta.
At max, initialize best. For each o:
  worst = inf
  for e:
    v
    if v<worst
    if worst <= alpha break (this own action can't beat current best)
  best=max
  alpha=max.
Good.

At brawl, maybe sample 2 scenario sets:
- all enemies best
- one or more enemies aggressive? Search deterministic.
Root risk handles.

Could create scenario enemy choices as best and second-best mix only for nearest threats:
At brawl, for each root own action, exact simulate under:
  1 all best
  2 for each of up to 3 closest enemies, set that enemy to each of its top2 while others best.
Take minimum / weighted.
Then rollout all best after.
This robust to local threat.
Integrate brawl search:
At recursive state, enemy fixed top1.
At root after initial move, scenario evaluation recursive.
But recursion function can accept `root_scenarios`.
Simpler `score_brawl_root(oa)`:
- base vector actions best
- evaluate path with search_brawl at depth
- for each nearby enemy and alternative top2, evaluate same depth, take min maybe 0.7*worst+0.3*base.
Depth recursion then deterministic.
This multiplies ~7* search.

Could use fixed simulation path rather than recursive after root:
For each scenario, simulate depth rounds with our greedy selected recursively? Need our future decisions.
`search_brawl` own branching depth 3 per scenario maybe okay 4^3*7=448, each nextstate 11 snakes. Deadline.

Cache enemy action policies at root, during next states recompute.

Evaluation caching important.

Iterative:
- Compute root own actions and preliminary scores.
- Always evaluate depth1.
- For duel depths maybe 2 then 3 then 4 until deadline.
- Brawl depth 1 then 2 then 3.
Depth measured rounds, root included. Search called initial depth means after each root move then depth-1.
- Keep best action from completed deeper iteration; update ordering.
- If timeout, return current best (from prior completed), but if timeout within first depth, prelim.

Root baseline immediate score can use `score_move`.

Need detect time exception:
```
class Timeout(Exception)
def check():
 global node; if node&255==0 and process_time()>deadline: raise
```
At decide catch.
But if timeout during an iteration, use previous best. Root preliminary exists.
First turn deadline maybe 0.7, later 0.042. Search may itself use 20ms; evaluation.

Potential process_time call starts before parsing. Set deadline based on turn:
`budget = 0.75 if turn<=1 else 0.042`. "第1回合1秒" likely decide invocation. Loading separate. Use 0.80.
Could use 0.045 risky; choose 0.041.

No stdout.

Global per-turn eval cache reset. `TURN_CACHE = {}`.

State conversion:
```
def parse_state(raw):
 snakes=tuple(S(... sorted maybe id))
 foods=tuple(sorted)
```
Class? Namedtuple standard. Class tuple overhead. Use tuple `(id, body, health, direction)`.
Own index find.

Directions global stored by id.
At state each call update before parse. Body cells convert tuples.
Infer:
```
for s:
 if id in prev:
  dx...
  if in VECT: d[name]
```
If body head same? impossible unless out? 
If id absent previous (never; no new snakes)
For self, if inferred use.
At turn1 directions default `"up"`? Need choose spawn escape. Single at (3,3), enemy (11,11). Brawl circle. We need opening direction.
At no direction and body stacked, candidate all for enemies; own can choose policy.
Our own default maybe direction from head to nearest food/space.
After choose store choice.

At next turn if returned but timeout? Our process global OUR_LAST_ACTION is action returned. Judge if exception none. Good.
If our selected move causes movement, infer.

If own action chosen is invalid reverse, judge forces prior. We avoid.
At very early, current own dir unknown, all action valid? If neck same coordinate, reverse ambiguity. Choose safe.

Potential direction inference when prior snake died absent no issue.
Raw IDs may not contiguous.

Food list duplicates? likely not.

Enemy initial candidate direction unknown. Policy dedup all.

Sim state direction update:
New direction for each surviving snake should be effective chosen direction. If invalid action, effective current. At initial unknown set choice.
Tuple dir.

Move effective:
```
neck=body[1] if len>1
if neck != head and add(d)==neck: return cur if cur else d
```
What if cur unknown at stacked and candidate direction goes to neck coordinate same head? No directional move has same coord, so no.
Once body unfolds, cur known.

Own current dir from inference.

Enemy policies with unknown dir generate all.

Preliminary own action:
- Avoid basic self wall.
- Score destination food.
- food manhattan.
- region after predicted enemy best maybe.
Could simply search depth1 computes detailed eval and risk.

Root action risk calculation:
Generate enemy candidate list all effective and `basic_survivable` maybe include all. For each:
- e new body; if own dest in ebody[1:], lethal body.
- if dest equal, compare lengths:
  If own length < e length => lethal
  if equal => both die (lethal)
  if own greater => own survives head-on, but could other enemy.
Risk weight:
  body collision 2
  equal/longer head 3.
Could include actions enemy wouldn't choose due self; if its action results enemy death by wall/body, enemy won't; filter `basic_valid`.
Potential enemy intentionally collision to kill? body collision kills us if we enter their body, enemy survives, so valid.
Head-on equal kills both, could be valid sacrifice; include.

If any own move zero risk, restrict selection to minimal risk bucket. This boosts safety but may overavoid unlikely enemy suicidal moves. Good.
Also "potential next enemy head can move to our next possible" handled search/eval.

Predicted enemy best at root:
Need top actions perhaps use `policy_actions`.
For brawl, fixed vector.

Evaluation function in detail:
```
def evaluate(st):
 key...
 own find else death
 enemies.
 occ_tail = ...
 count, fdist, seen_food = bfs
 need = min(board_area, max(length+2, int(length*2.5)))
 if count < length: -8000 - (len-count)*100
 elif count < length*1.5: -1800...
 score += min(count,need)*4
 if fdist is None: score -= 4000 + health*20 maybe
 elif fdist >= health: score -= 3000 + ...
 score -= fdist*(8 + (100-health)*0.2)
 if food adjacent...
 score += length*80
 score += health*0.3
 next mobility basic count*20
 enemy:
   d...
   if d==0 impossible
   if own_len > elen:
      if num_enemies==1: score += max(0,6-d)*30
      else if elen < ownlen-2: +...
   elif elen >= ownlen:
      score -= max(0,7-d)*(12 if duel else 6)
   enemy head targeting our possible moves? 
```
Length reward must influence ties but not seek food into trap. 80 each, trap penalty thousands.

Space cap score:
`space_need = max(24, min(area, length*3))`
`min(count, need)*3`.
If count large > need no extra.

Local mobility after resulting state:
for own effective dirs, dest in bounds and not obstacle body after tails maybe. Count.

Voronoi food control:
Maybe compute distances to all foods for own/enemy Manhattan and count own closer:
For each food:
- own dist approx; min enemy dist.
- +15 if own <= enemy and <= health.
This encourages food.
But Manhattan ignores body.
`food_score`: if own head food already eaten reflected length/health. For remaining, nearest.
Enemy competition:
if own distance <= enemy dist +? +8.

Aggression/collision:
Duel exact search.

Could add "kill proximity": If own longer and enemy's flood space low, approach.
Need compute enemy region only duel maybe. At eval, if duel compute enemy flood count cap; score += max(0, own_count-enemy_count)*2? To cut off.
Flood from enemy with own body obstacle. If enemy count < enemy length, it is trapped and likely dies, huge positive. This can drive containment. In brawl expensive; skip or cap.
Evaluation duel:
`ecount=region_count(enemy head, obstacles excluding tails, cap 120)`.
score += min(own_count,need)-... maybe difference.
If ecount < elen => +4000.
If our longer, proximity reward.
If not longer, distance.

Brawl region all only own due cost.

A* route safety:
Could use BFS to food with dynamic own tail. Static flood enough.

No food path due obstacles can trigger huge penalty even if moving opens path. Exclude tails all snakes allows opening one step only. A corridor blocked by non-tail body can eventually open as snake moves. Static could falsely no path. But food plentiful.

Move ordering preliminary:
`quick_action_score` uses dest food, Manhattan food, center, risk.
Then iterative result store root values and sort.

Search brawl:
At node, if depth 0 evaluate.
Own candidates from `legal_dirs(st, own)` not accounting enemies.
Enemy action map via top1.
Simulate each.
No alpha needed.
To increase robustness, at each own node perhaps include two scenarios for nearest enemy? only root.
`brawl_root_value(oa, depth)`:
  policies root top2.
  base moves.
  scenarios [base]
  For nearest up to 2 enemies:
    for alt top2 excluding best:
       moves base with alt.
  val each: next=sim; if depth>1 `brawl_search(next,depth-1)` else eval
  return min? worst is overly conservative. `0.65*base +0.35*worst` maybe avoid risky. If immediate death any plausible, risk already.
Use worst if alternative plausible. Could kill performance. top scenarios 5.
Then root candidate values.

At recursive brawl, enemies policy top1. This assumes.

Enemy policy top candidates:
Use `valid_dirs_for_snake`, but allow action into other current tail. Basic collision check dynamic tails.
```
body_after = move
if dest in body_after[1:] invalid
for others:
  obstacle cells o.body[1:-1] (because head and tail vacate)
  but if other tail duplicate, body[:-1] includes tail duplicate, blocks appropriately.
```
If dest current other head, all heads move, allowed. If other has length 1? min3.
If dest current own? self exact.
If outside invalid.
Score:
- food
- nearest food Manhattan
- open neighbor count using static body obstacles
- danger heads:
 for each other head:
   if manhattan(dest, oh)==? At next current simultaneous, not.
Head-on candidate action chosen based current heads: each enemy decides whether move to a cell. For policy snake S, another snake O may move into S dest if O head adjacent. If O length >= S => penalty; shorter => bonus. Approx.
- Avoid body adjacency? if destination next to longer body not relevant.
- Health urgency multiplies food.
- center.
Use deterministic tie hash.

At root strong opponents might select second due detailed flood. Top3 includes.

Could simulate all enemies "best" independently causing multiple choose same food/head collision exact.

Food respawn in simulation omitted. Evaluation after an eat has fewer foods; over horizon might no food and penalize route incorrectly. We should replenish eaten foods deterministically to maintain. Implement in next_state after deaths:
`needed = len(alive)+1 - len(remaining_foods)`.
Add cells not occupied/food using deterministic PRNG based state and turn absent. Sim state can include turn. Include `turn`.
Parse raw turn. next_state turn+1. Generate using xorshift hash from turn, iteration, maybe scan starting index.
```
seed = (turn*...+len(alive)*...)&...
for k needed:
 for step in range(area):
   idx=(seed + step*167?)%area
   if free add
```
This picks deterministic quasi random. Need no random module.
This improves.
State tuple `(turn, snakes, foods)`.

Food respawn occurs after dead disappear. Use final alive bodies.
If no free break.
At actual simultaneous two heads eat same food, one replenish.
In simulation, food spawn cell could be under a head? "random empty", bodies occupy; exclude all body.
Could spawn where dead vanished.

Evaluation turn can use max_turns/time pressure? End rankings if timeout: alive compare lengths. Near max turns, length becomes primary and safety less. State max_turns. Sim state include max turns maybe raw. Add `max_turns` global constant.
If turns remaining small, score length more. `time_left = max_turns-turn`; if <15, survival to end and length. length score perhaps 500. But decisions.
At terminal turn max: alive rank length. Eval length.
State max_turns in global parsed each call; pass via global MAXT.
If simulation reaches max_turns, evaluate with huge length emphasis:
`5000*length + maybe whether alive`. But likely.
Add state turn and if >= MAXT evaluate length*10000.

In actual placement, late game length matters among alive. Maintain food.

Head-on and length:
Eating to outlength enemy enables killing.

Possible exploit initial body stacked. Our opening should choose safe direction toward food. On 15 at (3,3), enemy far. All safe except perhaps wall? length3. choose nearest food.
Brawl spawn circle and 12 foods; maybe center crowded? Need avoid enemies.

Board coordinates and direction.

Advanced idea: Hamiltonian cycle for survival. On 15x15 odd area no full Hamiltonian cycle for rectangular grid odd, but can follow space. Food random. Flood enough.

Could implement long-term survival route via "tail distance": if no safe food, chase own tail. Evaluation maybe region.

Potential issue head-body collision with enemy's tail after it eats: We simulate candidate based dest food and append old tail, exact. Good.
Health order: move tail, health, food. Collision after food; our new body includes growth and may cause self collision? Standard snake can't head into old tail even if eats because tail popped then appended; head distinct. Could wrap in tiny space and head hits body.
Starvation before eating: Our next_state health decrement then if h<=0 mark dead, even if food. Correct.
Movement out and food no.
Head-head length after eating (grown) uses post-eat length. Rules eat before elimination, so yes length can be one greater. Use len(newbody).

Collision with bodies of snakes that simultaneously die uncertain. okay.

Head-head group:
If 2+ heads same:
- max len; all with less die; ties at max all die. One strictly longest survives.
Even if strictly longest also collided with a body elsewhere? Head cell same could coincide body segment of another not in group, then it should die too; our mark bodydead first and then head winners may remain erroneously. Example own head enters enemy body while also head-head with third; dies. Need body collision applies. So after body_dead, head group only among not body_dead? If a snake's head collides with body, it dies regardless. Remove before head resolution. If group all? fine.
Similarly wall/starve.
Then longest among remaining.
- Dead removed.
Food eaten by bodydead too before collision, correct.

If dead due body collision, its own body remains obstacle for others simultaneous. We built all post bodies before marking, good.

At current state, state only alive.

Enemy policy candidate into cell where another snake's current head is: current head vacates, but another could choose "reverse invalid" and still head moves current direction, no stay. Allowed. Could be head collision only destination not current.
Policy danger checks candidate destination from others.

Root risk enemy candidate body:
For each candidate, exact new enemy body. If own destination in ebody[1:], own dies if enemy survives, likely. Filter enemy basic wall/self but could die from other; still maybe not obstacle if dead removed simultaneous. Conservative.

Choose minimal risk:
Risk for head with shorter enemy isn't lethal for own but can kill enemy. In multi, if third longest etc. Root score positive.
For body risk always death.
If equal length head risk death both.
Minimal body/long risk count.
We can map risk categories separately:
`risk_bad`, `risk_win`.
Restrict to min bad, then max win perhaps.

What if no zero due enemy adjacent, choose.

Immediate predicted fixed simulation will also determine.

Root score fallback:
For each own action, enemy predicted best vector. `next_state`; if own dead - huge else eval. Add risk.
For duel minimax depth1 same.

Search own legal candidate generation includes action into known immediate enemy body; simulator terminal.

Potential policy recursion loops due repeated states no issue finite depth.

Time caches:
Global `EVAL_CACHE`, `POLICY_CACHE` keyed state? Policy result depends sid and topn; snakes and foods. Key can be `(sid,topn,snakes,foods)` enormous. Search node calls policies for each enemy each own branch; state same, cache valuable.
`policy_cache[(sid,topn,snakes,foods)]`.
But tuple hash cost. okay.
`eval_cache[(snakes,foods)]`.
Clear each decide.

`next_cache[(moves_tuple,state)]`? Root branches unique, maybe recursion repeated. Can cache. Key huge. skip maybe.

Basic BFS implement fast:
Bitboard and neighbor ids precomputed global per dimensions:
`NEIGH[id]`.
Since dimensions only 2 known, precompute lazily.
`blocked` int.
BFS:
```
seen=int bit head
q=[head]
dist array dict maybe layer loops
for depth in range(maxdist):
 nextq
...
count increments for cell not head
if food bit & bit...
```
Need return region count cap and food distance. We can continue until queue empty or cap and food found.
If count cap reached but no food, continue but don't count? Fine.
Food bit.
Passable if not blocked and not seen.
`blocked` includes all body except tail coordinate each snake. Need own head? if blocked start only no matter neighbors.
Maximum BFS full 961.
Food dist limit health-1 but if count still need region; BFS all. Evaluation calls one.
```
limit = min(health-1, 80)
found = None
while q:
  ...
  if found and count>=cap: break
```
If food farther than health irrelevant but can return >.
For enemy region, health irrelevant.
Count includes accessible open cells (not head). Region size possible area-1.

Obstacle tails:
```
for body:
 for p in body: bit
 blocked ^= tailbit? 
```
Duplicate: build without tail:
for p in body[:-1] block
```
This excludes last coord even if duplicate but body[:-1] includes duplicate same coordinate, so remains blocked. correct.
```
Include heads.

Could allow enemy tail next move. yes.

Food distance path entering own tail:
excluded only if no duplicate. If tail duplicate, blocked.

Immediate candidate `valid_dirs` self:
newbody before food. If dest in newbody[1:] => invalid, exact self collision after movement/eating. Even if food? body_after includes own segments; yes.
For enemy basic other obstacles as current `body[1:-1]`; but if another's tail duplicates, tail remains body because body[:-1] has coordinate, as said body[1:-1] includes duplicate except maybe length3 [H,T,T], slice [first T] block. good.
If another body length? yes.
Current own body tail moved exact.
Head current excluded.
Other snake may eat and tail not move, but policy unknown; our obstacle body[1:-1] excludes tail perhaps unsafe if enemy eats. At root risk exact candidate includes append if food. Good.
For policy candidate scoring, no need perfect.

Own root actions should not reverse due effective. `valid_dirs(st, sid, ignore_others=True)`.

When state body stacked, body[1] same head, reverse rule not triggered because move cannot same. current dir maybe unknown. all.

Quick food Manhattan:
```
min(abs...)
```

Potential opponent behavior tracking:
Could adapt based observed choices. We only know body each turn, infer actual enemy move. Track action frequency / aggression. Strong bots varied. Maybe opponent model could learn if they chase food or attack. Global per game:
`ENEMY_STATS[id]`: counts choices toward our head/food.
But one decision only 50ms; not needed. Could use history to predict exact:
- At current state, last state and current body gives enemy previous action. Their policy likely deterministic; learn features impossible.
- Preserve previous foods and actions to identify.
No.

Could use minimax duel and scenario brawl enough.

Late ranking:
Survival means not necessarily kill. In brawl max800, health forces food. Food count high. Area huge; likely most survive? 11 snakes length grows; collisions. Need claim territory.
Voronoi might matter. Add own region and food proximity.

Enemy proximity brawl: avoid longer, engage shorter only if nearby. Do not over-aggressive due third.

Aggressive trapping:
Evaluation enemy region duel helps.
Policy own search naturally may choose moves that lower enemy region if evaluation difference.
Could calculate cut potential.

Let's flesh classes and functions.

Constants:
```
D_ORDER = ("up","right","down","left")
V = {...}
REV = {...}
```
Snake tuple fields indexes SID=0 BODY=1 HEALTH=2 DIR=3.

`make_state(raw)` returns `(turn, snakes, foods)`, set globals W,H,MAXT, YOU, NEIGH, AREA.
raw body lists list ints.
Directions inference before.

Global dirs update:
```
old_heads
for raw snake:
 if id in LAST_HEAD:
  delta...
 else if id == you and OUR_DIR...
 DIRS[id]=...
LAST_HEAD...
```
Need direction inference can tell if previous head and current head difference. yes.
At turn1 no.
If id somehow direction missing, choose toward center? `default_dir` based spawn:
- if x < w/2 choose right elif > choose left; if y... This may head into center, likely.
For enemy unknown, policy generates all so dir irrelevant.
For own unknown, choose via scoring.

At parse, each snake dir from DIRS.get(id).

Update after choose:
`OUR_DIR = chosen` but if chosen effective? chosen from valid, yes.
DIRS[you]=chosen.
If process call times out after return no.

Potential module reload each game.

Neighbors:
```
def setup:
 NEIGH = [tuple...]
 CENTER_DISTS maybe.
```

State food sorted for hash.

`snake_by_id`.

`effective(s, action)`:
- current = s[3]
- if neck distinct and dest==neck and current: current
- else action
Potential reverse action when current None and neck distinct shouldn't happen.

`shift_body(body,d,foods)`:
nh tuple
nb=(nh,)+body[:-1]
if nh in foods: nb += (body[-1],)
return nh, nb, ate.

`next_state`:
```
actions = moves.get(id, dir or up)
infos
new_health...
food_eaten set
occ_segments = 0
for nb:
  for p in nb[1:]: bit
dead=set
for info:
 if outside or health<=0: dead
 elif headbit & occ_segments: dead
# But occ_segments includes own body and all.
alive_candidates
head_groups
for cell with >1:
 maxlen...
 if count max==1: others dead else all dead
```
Subtle occ_segments includes segments of snake itself including if duplicate head? Body index 0 excluded only one coordinate; if another segment same coord as head due collision, catches.
Wall positions not in neighbors.
Need map heads to list.
For group, max length.
If strictly max one survives.
A snake already dead excluded.
Food removal if any ate; all ate flags.
Health reset even dead.
Survivors tuple preserving current order.
Food:
`remaining = tuple(f for f in foods if f not in eaten)`.
Need set.
Respawn to len(alive)+1:
- occupied all body coords.
- `seed = ((turn+1)*1103515245 + len(alive)*... + sum head x...) & MASK`.
- for k needed:
  start = seed % AREA; step maybe `2*seed%AREA+1` not coprime potentially cycles not full. simpler scan `(start+j)%AREA`, up to 961. needed small.
  cell coord from idx.
  if bit not blocked and not food set.
  update seed = seed*... 
This may add food adjacent head but okay.
Sort foods for canonical.
Return.

Food spawn simulation can create food in square a snake's head just vacated final? final bodies all occupy, excluded.
No empty if full.

`valid_dirs`:
```
res=[]
seen=set
for a:
 d=effective
 if dup continue
 nh
 if out continue
 nb...
 if nh in nb[1:] continue
 res append d
```
If no res, return all in-bound or current to avoid external invalid. decide fallback.

Policy:
```
def policy_actions(st, sid, topn):
 s
 vals=[]
 for d in valid_dirs:
   nh,nb,ate
   score
   if ate +=100
   nearest food excluding eaten...
   score -= dist*(4 or 10)
   open around nh: cells in bounds not blocked (current all body[1:-1]?)
   score += open*5
   for o:
      od=manhattan(nh,o.head)
      if od==1 maybe o can move to nh? Actually O at distance1 yes.
      if olen >= len: -70*(...)
      elif len>olen+1: +25
   center score
   tie hash
 sort
```
Need an enemy baseline "looks at space". Add a cheap flood count only at root? topn selection globally. Could compute local tail corridor:
`open_neighbors`.
Maybe score region for top initial 4 costs 4*snake per node too much. At root policy top3 with flood could improve enemy prediction. We can have `policy_actions(..., detailed=False)`; at root call top3 detailed if duel. But recursive uses simple.
At current call root, for each enemy candidate compute flood count after moving? State not updated all, approximate. Cap30. For 10*4 40 BFS ~ maybe okay root but search calls policy cached root only. Use detailed only when `topn>1 and num_snakes==2`; Brawl top2 too maybe nearest.
Function can call `flood` on hypothetical snake tuple with others same, cap40. 4*10*961 ~ okay ~1ms each maybe 10ms. Only once root.
But policy cache key includes detailed.

For duel minimax deeper topn3 but simple after root? If policy function always detailed, costly. Pass depth/root.
`policy_actions(st,sid,topn,detailed=False)`.
At root detailed for all enemies? Brawl maybe only top2 for enemies within Manhattan <=8; far just top1. Could simplify all detailed cap30.

Danger:
For each other head adjacent to nh, if their possible move to nh. Any adjacent yes. Compare.
If equal length and head collision, both die, baseline avoids.
If our snake own length and policy enemy: enemy will avoid if own >=.
If enemy shorter than us, it avoids us.
If enemy longer, it may attack (+ score).
In `policy_actions` for sid enemy, `other` includes us; correct.

Scoring center:
Brawl baseline may center food; slight.

`region_food(st,sid,cap)`:
blocked build.
Start bit.
Food set may include under head? after state food never occupied, except simulation? referee spawn empty. okay.
Count accessible.
Layer BFS.
Use `NEIGH`.
```
if foodbit & nbit and fdist is None: fdist=dist
```
Food could be inaccessible due block.
Count only cells. `count>=cap` continue for food up to health.
Stop when found and count cap.
If queue empty.
Return.
```
healthdist_limit = max(0,min(health-1,90))
```
Even if no food within health, nearest beyond doesn't help; return dist anyway.

`evaluate(st)`:
Check cache.
Turn terminal:
if own absent death.
if no enemies `WIN_BASE + length*...`
if turn>=MAXT: length*20000 maybe.
Flood own.
Need cap `min(AREA-1, max(60, length*3, 80))`. Duel perhaps max 225. Brawl own relevant region cap120; full region could 800 but no need.
Score.
Food:
- if fdist is None: -7000
- elif fdist >= health: -4500 - (fdist-health+1)*200
- distance penalty:
 urgency `(120-health)/100`
 `-(6+20*urgency)*fd`
- If health<15 and no immediate food big.
Space:
```
if count < length:
 score -= 6000 +...
elif count < length+4: -2500
elif count < length*1.5: -700
score += min(count, cap)*2.5
```
Cap value.
For brawl if count > 150 saturated.
Mobility:
Generate own valid dirs ignoring enemies maybe 50 each.
Enemy:
- head distances.
- relative.
- enemy region duel.

Food ownership:
for each food maybe max 12:
 own manhattan; min enemy.
 if own_d < min_e: +10; if own_d<=health.
 But own fdist BFS already.
 Could add sum inverse to prioritize contested food:
`score += 30/(own_d+1)`? Use int.

Center:
No fixed. Region handles.

Enemy region duel:
`eregion,_=flood(... cap=max(50, elen*3))`.
score += (min(owncount,cap)-min(eregion,ecap))*2.
if eregion < elen: +5000.
But region from enemy may be small due our body; good.
If own longer, distance closeness:
`score += max(0,7-d)*35`
if own length <=:
`score -= max(0,7-d)*25`
If much longer but enemy can avoid body. Fine.
Brawl:
if d<=3:
 if own_len > elen+1: +20*(4-d)
 elif elen>=own_len: -30*(4-d)
Also "enemy tail chase" no.

Length:
`score += length*70 + health*0.2`.
At late:
`time_left`; if <20 length*extra 250; safety still.

Potential score chooses head-on kill if shorter? simulation gives enemy dead and own survives if strictly longer, huge no enemies in duel. Good.

Terminal score:
```
if own missing: return -10000000 - depth? evaluate lacks depth
```
Search terminal handling after next state:
```
v=evaluate
if own dead v -= depth*1000? 
```
Evaluate can use turn: later turn less negative:
`-10000000 + min(turn,MAXT)*1000`, but absolute actual turn always later. Good. In same turn comparison depth not.
Win `10000000 - turn*?` but sooner actual smaller turn should higher; `+10000000 - turn*1000`.
Search values across same root/horizon.
`evaluate` death turn current.

At max turn, own alive: `500000 + length*10000` plus relative lengths.

Search:
Global `NODES`, `DEADLINE`.

`terminal` own absent or no enemies or turn>=MAXT.

Duel:
```
def search_duel(st, depth, alpha,beta, rootdepth maybe):
 check_time
 if ...
 eid
 oacts=valid_dirs own
 eacts=policy_actions(... topn=3 if depth>=? else 2, detailed=False)
 if none...
 best=-INF
 for oa in ordered:
   worst=INF
   for ea:
      ns=next_state
      if depth<=1 v=eval else recurse
      if v<worst...
      if worst<=alpha: break
   if worst>best...
   alpha...
 return
```
At root action ordering from `ROOT_ORDER` list. At deeper quick sort by maybe food.
Topn at deeper 3; branch.
Can reduce enemy actions based root? Opponent adversarial all plausible. 3.
Own actions maybe 4.
Depth selection:
- iterative `maxdepth` 1.. maybe 6, until time.
Each iteration recomputes; okay.
At each root, return values. Root depth `d` calls search with depth d where root included? Implement `search_duel(st,depth)` considers one round if depth>=1 then recurses depth-1. Root value. Good.
Store completed root values.
Need return best from current complete. For timeout during new depth, keep old.
At depth1 policy detailed? precomputed root enemy candidates detailed.
Could call `root_enemy_actions` global in search when st==ROOT_STATE? Comparing tuple. Simpler `policy_actions(..., detailed=(st==ROOT))`.

Move ordering at deeper:
Use `quick_dir_score` maybe.
Root order based preliminary and previous values.

Time check every 128 nodes.

Brawl:
`enemy_plan(st)`:
for each enemy `policy_actions(topn=1,detailed=False)[0]`.
Cache policy.
`search_brawl(st,depth)`:
- max over own actions
- moves enemy plan + own
- recurse.
Root scenarios:
At decide for each oa:
 baseplan.
 `vals=[]`
 base val recursive.
 For each of up to 3 threatening enemies:
   alternatives policy top2 detailed? Build.
   if alt != base val.
 score maybe min(vals) or weighted.
If scenario count grows, time.
Could create root plan variants only one alternative:
- all best
- all second (unlikely)
- for each nearest 2 each second.
At depth d, each calls recursive. At depth1 eval 6*4.
Depth2 each recursive 4 own= ~100 sims.
Depth3 ~400.
Good.
`brawl_root` checks time and computes scenarios sequentially; if timeout old.

Need not use minimax after root, but okay.

Iterative depths:
Duel likely `for d in range(1, 8)` but each deadline. Need avoid a too deep iteration consuming all and leaving no better but old okay. CPU time may exceed deadline by <= check granularity. Use 0.039.
Could estimate:
- Set max depth based snakes and area.
- Run d1,d2,...
At first turn more.
Maybe d up to 5 later.
Brawl up to3 later, first 4.

A potential issue every iteration root values updates; sorting. We should only accept depth>=2 if completed all actions. Catch timeout means discard.
Initialize root vals from `fallback_root_scores` without recursive. Then d=1.
`fallback` could call next_state base and eval; same as d1.
At timeout in d1, maybe no vals? calculate simple quick scores with no eval and risk.
We can guarantee return.

Root action risk:
`root_risks` before.
Filter min bad.
If tie, perhaps restrict top.
How incorporate search:
After values, `value += risk_win*... - risk_bad*...`, but if already filter min bad.
Set candidate list min bad.
If all same no effect.
Risk win add +300*count to fallback; in search enemy alternatives may simulate kill.

Risk categories exact:
```
def root_risk(st,oa):
 own new head/body before
 for enemy:
  for ed in valid_dirs:
    enh,enb,eat
    if ownhead in enb[1:]: bad += 2
    elif enh == ownhead:
      if len(enb)>=len(onb): bad += 3
      else: good += 1
```
Potential own head into enemy head? Both destination same. Strict.
If own action destination is current enemy body but tail moves safe, exact.
If own head in enemy post body due own? yes.
Count.
If enemy candidate is invalid due its own dynamic interactions but valid self.
Cap.

Root preliminary quick:
```
score = food*500 - manhattan*20 + open*...
- bad*100000 + good*500
```
Candidates min bad anyway.

Choose tie:
At end if best values close, choose action with:
- current direction bonus (less unpredictable?) no reason.
- food.
Use deterministic.

Deadlines and time:
`time.process_time()` allowed. Do not import os etc.
At decide top:
```
try: return decide_inner()
except: return fallback safe
```
Never raise. Fallback picks first valid from raw.
Need if internal code bug self-check would not error due catch, returns direction; but should know. Better broad catch avoids self-check failure but could hide. We need code syntactically valid.

Global state if exception, fallback static.
`emergency_move(raw)`:
- infer own body, current global.
- choose dirs not wall and not self after tail; maximize adjacent open.
- no file.
Always valid.

If decide returns wrong no.

No use print.

Let's consider exact direction invalid: Our `decide` returns action. If our chosen action is reverse due unknown current but neck distinct, valid_dirs effective maps to current. It may return reverse string; judge then forces current. Our `OUR_DIR` should store effective direction not returned? We choose d from valid_dirs which is effective. If original candidate reverse mapped current and dedup current, we return current, so fine.

Enemy dir update after no prior. At state current, policy all.

Initial open move. fallback scoring center can choose right from (3,3), good.

Let's test mentally state example own body [9,3],[9,4] so current direction up inferred if prior. valid reverse down maps up. Good.

Flood blocked and food BFS:
```
blocked=0
for body:
 for p in body[:-1]: bit
```
This includes enemy heads and own neck, excludes last. BFS start's own head is blocked but doesn't matter. A neighboring cell maybe current own head? no.
Food at head? none after state.
Queue seen includes head bit even blocked.
Distance layer.
Count.
If cell is enemy tail and duplicate remains blocked due body[:-1], good.
A food can be on a tail? referee random empty, no.

Enemy region from head includes tail open.

Search state body health:
Food append exact:
```
base = (nh,) + body[:-1]
if ate: base + (body[-1],)
```
For old body duplicate tail, e.g [a,b,c,c], move [n,a,b,c], if no eat. correct. If eat [n,a,b,c,c] length5. Correct.
Start [s,s,s], move [n,s,s], correct.

Collision timing and own reverse in initial:
Old [n,s,s], move back [s,n,s], head s in newbody[1:]? newbody[1:]=(n,s), yes self-death. valid excludes. Good.

Policy basic other body:
`blocked_dynamic`: for each other body positions `body[1:-1]`. Suppose enemy other tail not duplicate, vacates; safe. head vacates. If it eats, tail stays; policy might underestimate, root risk exact.
For valid enemy candidate itself use exact self newbody; good.

Policy candidate into another current head position allowed. But if that other snake's invalid reverse means it still moves; no heads stay. yes.

Enemy policy candidate into own current head? For other enemy action, own moves; head-head only if own chooses remain impossible. Could allow.

Simultaneous body collision:
After movements, if head enters a cell that was a head but head moved, not body unless new body includes old head at index1 (it does! Wait snake body after moving: new body [newhead, oldhead, oldsecond,...]. So if another snake head moves from oldhead A to B, A becomes its neck/body. If our head moves into A (the cell the enemy just vacated), that's collision with its body, not allowed. Correct dynamic: can't follow head, only tail. Our `next_state` catches because enemy new body[1] = oldhead. Policy basic other obstacle body[1:-1] includes oldhead? For current body, `body[1:-1]` excludes current head, so it would wrongly allow destination current head A. Need obstacle after move for other if unknown direction: old head becomes body regardless direction, so destination current head is always enemy neck after it moves. Thus should block other current heads! Except heads can move into same current head? The owner head vacates but body neck occupies. So yes current heads are unsafe body destinations. Head-head collision is based destination, not old head. Policy should block all other `body[:-1]`? Their tail may vacate, so positions old head through second-last remain body. `body[:-1]` exactly includes current head and all except tail, but duplicate tail caveat: if duplicate tail, old tail remains, body[:-1] includes one tail anyway. Good.
For each other, static after-move body guaranteed subset current body[:-1] (unless movement? old head always neck). If other dies? but policy. So block `body[:-1]`.
Similarly root risk exact e_newbody[1:] confirms current head.
Thus valid_dirs for a snake only checks self exact. Policy candidate filter dest in other body[:-1]. Good.

For our root preliminary, exact sim.

What about enemy candidate destination into another snake current head: body collision after other moves, so death; policy avoids. Good.

Flood blocked all body[:-1] correct.

Head-on enemy possible destinations from current head, policy danger.

Enemy policy open neighbors should use all body[:-1] obstacles, so current heads blocked (future bodies). correct.

`blocked_after` helper:
```
for body: for p in body[:-1]
```
This is guaranteed occupied next before considering growth; tails excluded unless duplicate. For current region after state, same.

Food path: If food lies on current tail, impossible because foods empty at start; tail may open. good.

One nuance: two snakes heads simultaneous food both eat, growth. next_state.

Respawn deterministic uses state turn; okay.

Policy food score:
If ate candidate, both length and health, big.
Food candidates contested: another head adjacent also can eat same, both eat, no loss unless head-head length. Danger scoring.

Policies root:
Detailed flood after moving:
Construct hypothetical st with only that snake body updated, health maybe. But other snakes not moved; blocked uses other current body[:-1], which models them moving. Own moved body. Food if ate remove? no.
`region_count` with body tuple. Could score.
But topn enemy actions should consider current food and hazards. Use.

Root plan brawl for each enemy detailed? To save, top2.

Search policies at deeper if `topn=1`, simple. In duel adversary at deeper should top2 simple.

Evaluation mobility `valid_dirs` could include reverse mapping, okay.

Own candidate in search perhaps only valid ignoring other; yes.

Potential search returns suicidal action because enemy policy at future avoids us but head collision group exact.

Root risk filtering can prune action that enemy could body-block with an action; strong.

Brawl scenario:
Need root plan policies computed once:
```
ROOT_POLS[eid]=policy_actions(root,eid,2,True)
```
For each oa:
 vals.
 base moves.
 scenarios for nearest enemies sorted by distance to destination perhaps.
 Evaluate:
```
def rollout_after(ns, depth):
 if depth<=1 eval
 else search_brawl(ns, depth-1)
```
At `search_brawl`, all enemies top1 simple.
At root scenario, if enemy alt makes enemy die immediately, next state removes; may be unrealistic if suicidal. Policy top2 should be plausible.
Value combine:
- If any val <= -TERMINAL/2, candidate value min.
- else `0.7*base+0.3*worst`.
Maybe robust ranking means worst.
Use `min(base,worst)` to avoid.
But alternative enemy move may sacrifice to cause tie; avoid.

At recursive search own action order based quick.

Time cache.

`TIMEOUT` class.

`check_time` increments:
```
if (NODES & 127)==0...
```
NODES global int.

At each eval maybe no check.

Iteration management:
```
best_vals = quick fallback
for depth in range(1, maxd+1):
  try:
    vals=root_search(depth)
    best_vals=vals
  except TimeoutError:
    break
```
But `root_search` may set some partial global no issue.
Before deeper, sort actions by current vals.
Deadline remains.
Duel root search itself alpha beta. To retrieve root values, cannot just call search for each action separately due repeated. Implement `root_duel_values(depth)` loops own actions and min enemy actions. Use alpha across own. Return dict if complete.
At deeper search recursion.
Enemy actions root detailed once.

Alpha:
```
best=-INF
for oa:
 worst=INF
 for ea:
  ns...
  v=...
  if v<worst...
  if worst <= best: break
 if worst>best...
```
Alpha same best.
Return.
At depth1, `v=evaluate`.
`depth` means root round then if depth>1 recursion.
At recursion similar.

Root enemy list all top3. If enemy no valid, `[enemy dir]`.

Brawl root scenarios can be expensive, checks.

Quick vals:
Need ensure own actions all. If none, return current/in-bound.
Calculate static candidate:
- food +300
- nearest food
- open neighbors using blocked
- center maybe.
- risk.
No BFS to guarantee quick.
Sort.

Risk filtering:
```
minbad=min
acts=[a for a if bad==minbad]
```
Then values only those. If selected list excludes some but okay.
If minbad>0 and all.
Store risk dict.

Potential risk count includes enemy action that is reverse invalid? valid_dirs effective dedup yes.
Enemy action causing it to hit our current body? It may still valid self; if it dies but our action safe. Head destination own body? Our own current head becomes body after our move, so enemy moving into our old head collides our body; does not hurt us. Fine.

Enemy action head dest equals own new head and enemy shorter: own wins. But if own head also collides with a third body, simulator.
Root `good`.

Enemy action causing enemy self-death excluded via valid_dirs; can still die on another but plausible.

Duel enemy policy:
If own longer, enemy policy avoids head-on; but adversarial opponent may see no escape and choose. Top3 likely.
If enemy longer, policy scores attacking +? In `policy_actions`, other own length shorter, for sid enemy:
```
if len(s)>len(o)+? += aggression based adjacent destination
```
Need score. Candidate nh adjacent to other head means other could move into nh too; if sid longer, head-on winning, score +50. If other shorter.
Also proximity to own head itself: food/attack.
Add:
```
if len(s)>len(o): score += max(0,5-dist(nh,oh))*15
else -= max(0,5-dist)*20
```
For sid longer, chase.
This makes top candidate attack.

For brawl enemy longer may chase us, scenario captures.

Own evaluation food ownership:
Could be killed while chasing.

What does "n名次拆成两两比较" mean ranks; survival primary. Our score survival huge.

Potential end with multiple alive at max turns, length ranking. Evaluation near end.

Max turn simulation if at `turn >= max_turns`: The decide at turn max is about to execute last round. Next state turn+1. Evaluate terminal. Good.

Opening raw state turn1 and max.

Emergency:
```
def emergency(raw):
 body...
 for D order:
   if reverse and known skip
   nh in bounds
   nb...
   if nh in nb[1:] skip
   score number neighbors in bounds not in blocked current bodies[:-1]
 return max
```
No exception.

Need ensure only standard lib imports `time` maybe math? no random needed.

Let's consider computational details and possible bugs.

Cache key:
State = `(turn, snakes, foods)`. Eval turn matters, include.
`EVAL_CACHE[st]=v`, tuple nested hash.
Policy key `(sid, topn, detailed, st)`.
Plan key st.
Python recursion depth max depth <=7 okay.

`next_state` actions dict keys int.
When policy actions uses valid dirs and `effective`; direction can None.
If no valid:
- Return effective current if in bounds? If all self/wall, snake doomed. For simulation choose current/up.
```
return [s[3] or "up"]
```
Even if wall, sim death.

Food append uses `foodset`; state foods tuple.
`eaten` set positions.
Heads outside could be in food impossible.

Occupancy collision:
```
seg_bits=0
for nb:
  for p in nb[1:]: seg_bits |= bit
```
If head outside, cell_bit function called? Skip for obstacle? body positions except head are in board (head is only outside). fine.
For own head bit if outside skip.
Starve etc.

Head group dictionary key bit.
Among not dead.
Strict max:
```
if len(winners)==1:
 for sid in group if sid != winner dead
else all dead
```
If group includes 2 and one bodydead, only one alive candidate => no head-head elimination, but its head same cell as bodydead snake's head. Rule simultaneous, dead snake's head still perhaps should count. We exclude, potentially lets own survive when tied with a snake that also hit body. Correct adjudication uncertain. Simultaneous suggests even bodydead heads may count. Could count all heads regardless other death. Suppose A head hits B body and same cell as C head; A should die; C survival not impacted. If A and C same length, would C die due A? Heads did enter same cell, yes "two or more heads into same grid; longest survives; same length all die." Even if A independently dies, C likely also dies. So include all non-wall? Starved heads also still enter. For own safety, conservative count all. Strict max could be a snake already bodydead, then no actual survivor; others die. Implement head groups among snakes not wall? Even wall head not in cell. Starving can count. Body collision can count.
Use all with in-board heads and health>0 maybe. If starved, dead but head entered. Simultaneous, count. Include all in-board. If strict longest is bodydead, it "survives" headhead but already dead; others less die. This is realistic simultaneous. Mark.
Thus:
```
groups for all in-bound, regardless dead
maxlen; if tie add all; else add all except maxsid
```
Even maxsid already dead.
This may be harsh. Fine.

A snake's head enters same cell as another head and also that position is body segment of third -> both likely body collision before.

Food removal before death okay.

Dead disappear after.

Respawn seed:
```
occ bits all survivor bodies.
pool_needed
idx = (seed + scan) % AREA
```
Food positions cannot overlap.
Sort may cost tiny.

Evaluation with no enemies before flood returns win, so doesn't chase length at max? If kill last enemy before max, game ends immediately, win. huge.

Score terminal death:
`return -9000000 + min(st.turn,MAXT)*5000`
At turn bigger, less negative. At simulation horizon turn root+depth; prefer later death.
Win `9000000 - min(turn)*5000` sooner.
Maxturn:
If own alive, score based relative:
```
5000000 + length*10000 - max enemy length*5000 + health
```
But if all alive at end ranking. This could dominate normal. Good.
If no enemies win checked first.

Depth horizon not max, normal.

Enemy region evaluation calls `region_food`; maybe EVAL cache.

Brawl root policies detailed may consume first deadline before search. Deadline set at start and check only inside policy? BFS no check. Worst 40*961 ~38k neighbor loops, <5ms.

First turn 0.8 can deep. Later 0.04.

Search depth tuning:
```
if n==2:
 maxd=7 if turn1 else 5
else maxd=4 if turn1 else 3
```
Deeper iterations may start near deadline and timeout; okay. But starting a too deep iteration can spend only until deadline, no harm. Check granularity 127 nodes.
NODES increment in search only; if tight loop next_state called then check after.
`check_time` at each search entry and root scenario.

Time budget 0.038 after parse/policy. Deadline set before parse, policy. Good.
At turn1 0.75.

Potential CPU time function resolution. okay.

Could adapt based num snakes alive.

Root search d1 might call evaluate 12 branches, each BFS. Fine.
Duel d5 worst 12^5 250k, deadline.
Transposition may help but no.

Evaluation score scale and alpha:
Use floats or ints. ints.

`policy_actions` detailed:
For each candidate, danger. Candidate filter:
```
if point_bit(nh) & blocked_after_without self? 
```
Build all body[:-1] for other only.
Self exact.
Open neighbors using `blocked_all`, but new own old positions differ. approximate.
Food distance Manhattan.
If no foods score.
Tie:
`tie = ((x*31+y*17+id*13+dirindex)&7)*0.01` score float. Return.
Could avoid floats.
Center: `- (abs(x-cx)+abs(y-cy))*0.2` maybe center can be crowded. Region more.

Detailed region:
Make temp snake with nb, health adjusted; state `(turn, snakes replaced, foods minus eaten maybe)`.
Call region cap40.
`score += min(region,40)*2`.
If region<len -> -1000.
This may select better.

Policy food target:
If ate, nearest excludes eaten.
Manhattan distance. If health low, coefficient.
```
coef=3 if health>30 else 12
score -= coef*ndist
```
Health post decrement.
Food ownership maybe.

Aggression:
```
for o:
 dhead
 if dhead<=6:
  if len(s)>len(o): score += (7-d)*8
  elif len(s)<len(o): score -= (7-d)*12
  else score -= (7-d)*8
```
This means shorter avoids.

Candidate head-on danger:
for each other, can other move to nh if manhattan(otherhead,nh)==1 (unless reverse impossible) then:
 compare post/eat lengths. We don't know other ate.
 if other len>= ours => -150
 else +30.
This is already.

Own eval:
Region and enemy dist.
Food contested:
```
for f:
 own md
 if own md <= health:
   emin...
   if ownmd < emin: += max(0,8-ownmd)*3
```
12 foods * enemies up to110 distance each eval, expensive. Skip or only nearest 3 foods.
Nearest BFS enough.

Evaluation mobility valid_dirs calls tuples. fine.

Enemy region in duel:
Use `region_food` second BFS. Evaluation nodes many, doubles cost. Maybe only at depth<=1? But eval all horizon. Duel branch manageable. It improves.
Cache region? EVAL.
Cap 80.

`region_food` health:
Pass sid, use health.
If evaluating enemy, limit enemy health.

Count BFS performance with bit ops and list:
```
while q:
 nq=[]
 for c in q:
  for nb in NEIGH[c]:
    b=1<<nb
    if not seen&b and not blocked&b:
...
 dist +=1
```
Food dist found when neighbor.
Count each added.
Start count=0 (region excludes head). If empty region count0.
Cap.
Continue if no found but cap reached; it still traverses. okay.
Stop if found is not None and count>=cap.
Food might be farther than health but found; eval penalizes.

Region could revisit body cells as snakes move; static.

Brawl evaluation one BFS full if no food. Foods many so stops after found and cap. If count cap quickly and food found, good.
Duel second.

Max turn handling before flood.

Root risk complexity 10*4*body lengths; length can grow hundreds, tuple slicing and membership `nh in nb[1:]` O(length) for each candidate. Snake length perhaps up to hundreds in late 800. Bodies 11* maybe thousands cells <=961, length can't exceed area but duplicates only temporary, total <=961 mostly. Python membership tuple up to 900, 40k ~ manageable but search huge late.
Optimize bitsets:
- `nh in nb[1:]` could be O(len). For self collision, use set? Body no duplicates except tail temporary; build body set each call expensive.
Could determine self collision geometrically: New head collides with own post-body if equals any old body segment excluding old tail (because new body[1:] = old body[:-1]). So `nh in body[:-1]`. Same.
Use frozen set per snake? State body tuple; cache body masks and sets. Build `body_mask` int, but duplicates impossible except tail. Check `mask_without_tail`: bit OR body[:-1]. Function with cache.
`MASK_WITHOUT_TAIL` dict keyed body.
`bit(nh) & mask`.
Much faster.
For exact enemy `enb[1:]` = old body[:-1] regardless growth? Newbody after eat `[nh]+old[:-1]+[oldtail]`; index1 includes old all including tail appended. Wait if ate, e_newbody[1:] = old body (all old coordinates). So root body collision mask depends ate:
- no eat: old body[:-1]
- eat: old body (old tail appended)
Use mask.
Self collision after own move:
- no eat: head vs old body[:-1].
- if eat: new body `[nh]+old[:-1]+oldtail]`, head vs old body all. Since tail appended, if nh==oldtail, collision. Can a head move into just-vacated tail and eat food there? Food cannot start on oldtail (occupied), so ate false. Thus self check no-eat enough. If food at head dest, not old body. Use old body[:-1].
Thus valid dirs bit.

Global caches per turn? Bodies in search many. `MASK_CACHE` global per decide or module? Body tuple hash and build O(len); useful across turn. Module persists game, max many unique but memory maybe thousands *; okay but global across games reload. Could grow over 800, each body unique. Search maybe. Keep `MASK_CACHE` with cap e.g. if >20000 clear.
`body_mask(body, include_tail)`.
Could compute:
```
m=0
limit=len if include else len-1
for p in body[:limit]: m|=...
```
Duplicate no issue.
`head_bit & m`.

Root risk enemy noeat/eat masks.

Policy other blocked after current body[:-1] use bit.
`blocked_after(st)` OR masks no tail.

Flood blocked same.

Occupancy collision next state needs segment bit; loops total lengths unavoidable. Could use masks:
for each nb, seg_mask(body nb excluding head) = OR nb[1:]. Build cache key `(nb,"seg")`. Unique; but compute.
Can compute during body creation? no.
Use `mask_range`.
Cache generic `(body, mode)`.
Cache size.
Potential body tuple up to 961; OR loop.

Respawn occupancy full body mask include tail.

Policy validity other:
`if nbit & other_mask_no_tail: skip`.
Current head included, as desired.

Self:
`if nbit & mask_no_tail(body): skip`.
If duplicate tail, no-tail includes first duplicate so blocks.

Root own new length:
`onb` via shift; check self valid already.
Enemy risk:
`mask = body_mask(e.body, include_tail=eat)` because post body segments:
- no eat old body[:-1]
- eat old body all.
if own head bit & mask -> bad.

Head collision lengths len(nb).

Valid dirs:
`d=effective`.
`if nbit & no_tail`.
Outside.
No need create nb.

Policy action filters other masks.

Emergency similarly.

Body mask cache key include mode maybe `(body, include)` tuple hash body once.
`get_body_mask(body, include_tail=True)`.
If include false use slice tuple as key? body[:-1] creates tuple. Could key `(body, False)` and loop range len-1.
Cache dictionary key tuple containing body; okay.

Food bit global `food_mask`.

Neighbors precompute.

State foods sorted tuples.

`next_state` health order:
```
moved records dict/list
for s:
 d...
 nh...
 ate
 nb...
 nhlim...
```
Even if health0 and ate, dead; health reset but mark based prehealth<=0. Store `starved=(h-1<=0)`.
For group len(nb).
Wall.
Dead set.
Segments bits all moved.
Body collision.
Need if head in board and headbit & segs.
Head groups list all inboard.
Head-head:
- group len>1
- max length; count.
- if one strict: all other IDs dead.
- else all.
Dead already.
Survivor s if id not dead.
Food spawn needed based survivors.
No issue actions missing (shouldn't).

`turn` increment even max.

`state_snake`.

`enemy_ids`.

`quick_score`: no body shift:
- bit destination
- food.
- nearest manhattan.
- open count using blocked after all.
- risk.
- center maybe.
Potential current direction maintain +2.

Root candidate minbad. If quick food chooses.

Fallback root and search:
```
vals={a:quick...}
if candidate not all, only.
try:
 for depth...
```
`root_duel_values` loops candidate in ROOT_ORDER.
Set global ROOT_ACTION_ORDER.
At recursive own actions sorting:
```
acts=valid_dirs
if st==ROOT? root handles
else acts.sort(key=quick_state_action, reverse)
```
`quick_state_action` calls if food and distance, no risk.
For alpha, good ordering.

At duel root enemy actions:
`policy_actions(root,eid,3,True)`.
In recursion:
`topn=3 if depth>=2 else 2`
Maybe branch.
Could include all 4 at root if only small:
topn=4 detailed? Strong adversarial. 4*4=16 vs12. Use 3 to time. Risk considers all immediate.
At later node, an enemy's only killing move might be low policy due food; top2 maybe miss. Opponent objective survival, but adversarial minimax should include all non-obvious. Could use all 4 in duel! 16^d huge but alpha. Top3.
Add force-attack candidates likely score high if longer. If enemy equal sacrifice can head-on; policy equal penalty, may not top3 if 4 and one is attack. Root risk protects first, but future. Could top4. Depth reached maybe 3. Strong safety > depth. Use all 4. Opponent strong but won't choose self-death; valid dirs up to4. 16 branch. Deadline iterative.
At recursion dedup.

Duel `root_duel_values` uses all enemy valid.
Could order enemy descending. Min.
No policy candidate issue.
At brawl impossible all.

This makes duel robust to arbitrary one-step adversary, but evaluation assumes future.

Root risk for duel redundant.

Brawl enemy scenarios top2.

What if own candidate causes enemy to have no valid actions but still moves and dies, sim.

Policy plan cache:
```
def enemy_plan(st):
 key
 for enemy:
   acts=policy_actions(...1,False)
```
At root scenario use detailed cache separate.

`brawl_search`: check time, terminal.
Enemy moves fixed once.
Sort own actions by quick.
best.
No alpha.
At depth1 eval each next.
NODES.

`brawl_root_values(depth)`:
Precompute root policies for each enemy top2 detailed once outside.
For each oa:
 scenarios:
 base.
 Determine threatening enemies sorted by:
 `manhattan(o.head, own_dest)` or head current dist and length.
 up to 3.
 For each eid, alt second:
  plan variant.
 Maybe also plan where enemy chooses move that can collide with own destination:
    among all valid enemy actions, if dest==own dest include even if not top2. `policy_actions top4 detailed`; alternatives.
Use top3 root.
Scenarios max 7.
For each, sim then recurse depth-1.
Combine worst and base:
```
if base <= DEATH...
v=(base*2+worst)//3
if worst<base-100000: v=worst maybe
```
Use `min(base, (base+worst)//2)` essentially.
Maybe candidate safe in base but vulnerable alternative. `0.6 base+0.4 worst`.
If worst death terminal, value near death => avoid.
`vals[oa]= (2*base + worst)//3`.
Scenario alternatives only second may not include attack. Add all enemy actions that threaten:
for each enemy, `policy_actions(...,4,detailed=True)`, include any ed with head dest==own dest or own dest in enemy post body; up to one.
Detailed 4*10 okay.
Root policies list.
For each nearby eid, alternatives all actions excluding best up to2.

Brawl evaluation root scenario count 1 + 3*2=7.

Depth d root. If timeout, discard.

Fallback `base_plan` if enemy no.

Decision values include quick risk good:
After iterative, add `risk_good*100` maybe. Risk bad candidates filtered.
Tie random? deterministic.

Potential all candidate values equal due no time; quick.

`decide_inner`:
```
setup globals, update dirs
st=parse
acts=valid_dirs
if not acts emergency
risks...
minbad
cands
quick vals
best_order
TURN_CACHE...
maxdepth...
for d...
except Timeout
best=max(vals)
DIRS[you]=best
return
```
Clear caches before search, but body mask cache retain.
Set `ROOT=st`, `ROOT_CANDIDATES`, etc.
If no time, quick.

Use turn1 max deeper:
- duel later maybe depth5, first7.
- brawl later3, first4.
Maybe d1 always.
At d1 root values detailed eval.
If maxd loop, `root_values` catch.

If timeout during iteration, some evaluation caches remain but discard vals. Next call process new state anyway.

Catch all outside and emergency. But `TimeoutError` custom inherits Exception, caught.

First action direction global:
At decide end `DIRS[you]=best`.
If best is action string.

If decide gets exception before direction update but broad outer `emergency`, set dir there? emergency can.

Need not use `nonlocal`.

Let's inspect rule head-body collision tails:
Tail retract step1, so head can follow another tail. Our post body excludes old tail if no eat, includes if eat. exact.
All snakes eat after move, and if two heads same food both grow. exact.
Health reset before elimination length includes growth. exact.

Could exploit that health reset but collision still death no.

Food respawn in search random unknown; deterministic approximation.

Opponent IDs and you maybe snake list unsorted. Preserve list order doesn't affect simultaneous outcome. Policy loops.

Flood blocked after state with all body[:-1]. For own body no-tail, can path into tail next turn. Enemy tails too.

Area count not accounting other heads future body, but does include.

Space thresholds:
Length may exceed region due duplicates but body occupies unique cells. max length area.
`cap = max(50,min(AREA-1,length*3))`; brawl cap maybe 150:
```
cap=max(50,min(180,length*3))
```
Duel cap=AREA.
If count < length trap penalty. But static region excluding own non-tail; if snake is coiled, accessible region may be <length while it can survive by following tail. Food in same region and BFS distance matters. Penalty okay.

If no path to food due enemy wall but enemy will move, huge penalty avoids.

Enemy region comparison.

Evaluation exact:
```
base = len*75 + health
base += min(count,cap)*3
if count < length: base -= 7000+...
elif count < length+3: -=2500...
if fd None: -6000
else:
 if fd >= health: -...
 base -= fd*(8 + (100-health)//8)
```
At health100, coefficient8; at health20 coefficient18. Food 100 steps coefficient.
Nearest BFS path can be 0? no food under head after eating removed and respawn after; could respawn elsewhere. >=1.
If health1 and no food distance<1, fd >=health penalty.
`if health<=12 and fd>1` extra.

Enemy:
Duel:
```
d=manhattan
ediff=len-own
if own>elen:
 base += (eregion diff)*...
 base += max(0,8-d)*25
 if d<=2 and own>elen: +300
else:
 base -= max(0,8-d)*(35+diff*5)
```
But if enemy far.
If enemy trapped +5000.
Brawl sum proximity:
```
if d<=5:
 if own>elen+1: +=(6-d)*12
 elif elen>=own: -=(6-d)*18
```
Could prefer near shorter to kill but third.

Mobility +30*num.

Late:
```
left=MAXT-turn
if left<25:
 base += len*(25-left)*20
```
At turn max terminal separate.

Root risk head win:
If own longer and enemy possible head-on, not guaranteed. Add +250.

Quick center maybe no.

Brawl root policy detailed calls `region_food` with hypothetical `turn` and foods. `region_food` uses global caches? no.

Detailed score candidate:
```
tmpfoods = remove ate
tmp snakes replace body/health
region=region_food
```
Other snakes still old body[:-1] models their next occupancy. Good.
Health decrement.
If candidate ate, append old tail; region blocked includes duplicate old tail in body[:-1], exact.
No other movement new heads unknown.

Policy candidate danger body others:
We filter destination in other current no-tail, so can't enter body; could enter tail that stays if other eats. Detailed region does not account. Head hazard.

One issue enemy baseline may reverse action invalid; `valid_dirs` dedup effective. Good.

Directions inference:
At start raw turn maybe >1 but module reloaded? It isn't, one process per game. If exception timeouts no reload.
If global lost due module? no.
If a snake direction can't infer because prior head list not stored due first call? only turn1.
For own if previous action led wall death, game over no call.

Maybe judge calls decide only while own alive. yes.

Emergency fallback should not import state parse if globals W unset. Use raw width.

Code size okay.

Let's think if using time.process_time violates only stdlib no.

Potential self-check checks return exactly strings. yes.

Now maybe can improve with explicit safe path planning to food and avoid traps. Search covers few rounds. A* not needed.

Long-term starvation: health max100, food BFS.

Potential trap from own body: flood and search.

Could implement "tail distance" when no food:
If nearest food inaccessible/too far, follow own tail to stay alive. But if no reachable food within health, likely die anyway; following tail delays and food spawn can save. Evaluation no-food huge may choose arbitrary. Add score for distance to own tail: if no food, smaller distance better (tail opens). `taildist=manhattan(head, body[-1])`; base -= taildist*5 when fd none. If tail adjacent, can loop.
If food distance>=health, also.
Could compute BFS distance to tail excluded; Manhattan.
Add.

Potential region with food but enemy competing. okay.

Aggressive body block in duel: Evaluation enemy region may incentivize.

Head-on mechanics: Strict longest survives. Our search allows attack if longer. If lengths equal avoid. Length reward.

End length: Search horizon and food.

Should own policy choose food if it causes head-on vulnerability? risk.

Let's calculate immediate head-on group with enemy shorter:
next_state marks enemy dead, own survives. If no other enemies, evaluate win huge. Good.
If enemy body candidate also same? head group and body collision of own with enemy's new body cannot happen at same dest because dest is enemy head not body.

If two enemy heads plus own:
strict max maybe enemy longer than us but another shorter; max enemy survives, own dies. exact.
If own tied longest with another, all die. risk.

Simulation respawn:
Sort food tuples lexicographically; no issue.

Body mask cache:
```
BM_CACHE={}
def body_mask(body, tail):
 key=(body,tail)
...
if len cache>30000 clear
```
Key nested hash repeated. Fine.

Flood NEIGH global list. At parse setup if dimensions changed per game reload, but global maybe initial. `if W !=...`.

Food bit helper `cell_bit` assumes x,y tuple.

Manhattan.

State equality root for policy detailed maybe pass explicitly, no.

Root brawl `threat_actions`:
```
pols[eid]=policy_actions(root,eid,4,True)
```
For far enemies top4 expensive. Only policies all maybe.
Scenario only enemies with min distance from own head <=8 or length threat. Precompute detailed top2 for all because base best needed. Could call top1 for far, top4 for near.
Base best simple for all maybe detailed not needed. Strong enemy plan should include flood; use policy top1 detailed all once.
For alternatives nearby call detailed top4.
`policy_actions` detailed always computes BFS each candidate.
At root up to 10*4 BFS, okay.

`policy_actions` topn=1 detailed still computes all then top.

Quick state action:
```
nh...
score food*200-nearest*10 + mobility neighbor
```
No risk.

Search recursion policies simple top1, enemy movement may not be strongest. Evaluation safety.

Could introduce randomization to avoid predictability? Opponents are algorithms, simultaneous; deterministic might be exploited across thousands games/seats. Same bot vs same opponents many games. Random module seeded per game, could randomize ties. Strong deterministic fine. Could use random tie via random.random but consuming random perhaps affect referee food; avoid. Hash turn/body tie.

Opening could be predictable and exploited over rotations? Spawn positions rotate seats; no same coordinate always. Deterministic food random.

BT ranking across episodes.

Let's maybe add opponent model aggression tracking:
Global `ENEMY_AGGR` count: each update, infer previous enemy action and whether new enemy head moved closer to our previous/current head. If aggressive, policy aggression weight adjust.
At state update, for each enemy:
- prev heads and our prev head.
- current heads.
- if distance decreased, increment; if moved away decrement.
Over time.
Then policy for sid uses aggression factor:
`agg = min(3, ENEMY_AGG.get(id,0)*0.2)` maybe.
But adaptive opponent might just food path incidentally. Could.
Also stats whether enemy takes food.
Not necessary.

Could track enemy preferred policy and use last direction momentum. Strong snakes often continue unless food. Policy scoring add +3 for current dir. Currently tie only, so may turn toward food. Add +4 if d current, improves prediction.
At initial unknown no.

Enemy policy uses health from tuple.

Policy head threat:
```
for o:
 if manhattan(nh,ohead)==1:
   if len(o)>len(s): -=180
   elif ==: -=120
   else +=50
```
This makes enemy avoid own longer.
If sid longer, chase other head distance.

Own search sees enemy predicted.

Root risk restrict min bad may be too paranoid in brawl where multiple enemies can always sacrifice. But survival.

What qualifies "risk bad" for enemy body candidate:
If own dest in enemy post body. If enemy takes an action, its body could cross? Heads can cross but our head destination in a non-head body segment. If enemy action direction causes old head to neck; so moving adjacent behind enemy head is death. Restrict all such, good.
Head-on with longer enemy possible. avoid.

If own longer, enemy post body still kills us, so risk.

Quick action uses minbad.

Now code compile mentally.

Let's write code sections.

Imports:
```
import time
```

Constants, globals.

Custom exception name `SearchTimeout`.

`setup`:
```
def setup_board(w,h):
 global...
 if...
 NEIGH=[]
 for y...
```
Direction order maybe up/right/down/left. Emergency.

`infer_directions(raw)`:
global LAST_HEADS, DIRS, OUR_DIR
for s raw:
 head tuple
 old=LAST_HEADS.get(sid)
 if old:
   dxy...
   if in BY_DELTA DIRS[sid]=...
 # if sid == you and no DIRS and OUR_DIR...
newheads...
LAST_HEADS=new
```
If prior state missing own because died no call.
At turn1 set no direction.
Potential snake first move from spawn; at turn2 infer.
Enemy IDs dead retain DIRS but no harm.

Default direction maybe:
```
def default_dir(head):
 if x < (W-1)/2: right ...
```
Use in no valid sim.

State parse sets snake dir `DIRS.get`.
Food tuple sorted.

`OUR_DIR` redundant DIRS.

Outer decide:
```
def decide(state):
 try:
  return _decide(state)
 except Exception:
  try: return _emergency(state)
  except: return "up"
```
If W setup done, emergency.

_decide:
- start process time.
- setup.
- infer.
- root.
- own exists else return up (not called).
- clear eval/policy/plan.
- deadline.
- actions.
- risks.
- cands.
- quick.
- root globals.
- iterative.
- choose.
- DIRS you.
Potential direction update at start uses LAST_HEADS before choose.

If selected and judge deems reverse? actions effective valid, okay.

Emergency updates DIRS.

Root risk uses root food set.

`valid_actions`:
```
cur=effective_dir
for a in DIRS:
 d=...
 if d in seen...
 nx...
 if outside continue
 if bit & mask_no_tail continue
 out append
if not out:
 # choose any in-bound; if none current
```
Do not include invalid action names.

`effective_dir`: current = s[3]; if current and reverse destination equals neck. Compute neck and action dest. Need W bounds no.
```
if len>1:
 nx=head[0]+...
 if (nx,ny)==body[1] and body[1]!=head: return current
return action
```
If current None, action.
Even if action reverse and current direction itself would also maybe wall, exact.

`moved_body`.

`next_state` actions values maybe None.
For each snake:
`a=moves.get(sid)`; if None `a=cur or default`.
`d=effective`.
Need default uses global W/H.
Moved record list `(sid,nb,nh,h,ate,wall,starved)`.
Foods is tuple; membership set.
Segments:
`seg_mask_from_body(nb)` where exclude head include all rest. Use body mask? `mask_except_head`.
Implement generic:
```
def mask_body_range(body,start,end)
```
Cache key `(body,start,end)` perhaps.
`body_mask(nb,True)` includes head too, not.
`segment_mask`:
cache key `(body,"s")`; loop body[1:].
`notail_mask`.
`full_mask`.
Could create three caches dict keyed `(mode,body)`.
```
def mask_body(body, mode):
 key=(mode,body)
 if mode0 range 0,len-1
 mode1 range 0,len
 mode2 range1,len
```
Use integer mode.
Cache max.
For root risk enemy mask mode 1 if ate else0.
For self mode0.
Policy blocked mode0.
Respawn mode1.
Collision mode2.

Body tuple hash cache.

`next_state` group:
```
groups={}
for rec if not wall:
 bit...
 groups.setdefault(bit,[]).append(rec)
for:
 if len>1:
  maxlen=max(len(body))
  winners...
  if len(winners)==1:
    for rec if sid != winner dead
  else all dead
```
Even if head outside no group.
Health starved rec.
Survivors based original order and ids.
Food eaten set.
Potential `eaten` food cell by wall no.
Spawn:
```
need=len(surv)+1-len(rem)
if need>0:
 occ=...
 seed...
 for k...
   found...
```
`seed` hash heads:
```
z=(turn+1)*... + len(surv)*...
for s: z ^= ...
z&=...
```
Scan sequential.
Convert idx `(idx%W, idx//W)`.
No occupied.
Set foodset.
Sort.
```
return (turn+1, tuple(surv), tuple(sorted(foodset)))
```
Health reset 100 for ate even if wall, then dies.

Policy:
`blocked = board_block(st)` mode0 all.
For candidate:
- self check.
- wall.
- `otherblock` mode0 only others. Note blocked includes own old no-tail; dest self already. For open count use blocked.
- if nbit & otherblock skip.
This excludes other current head and body until tail.
- ate.
- nearest food after removing eaten.
- danger etc.
Detailed tmp state:
replace snake `(id,nb,max? health, d)`; foods remove.
`region_food(tmp,sid,cap=40, needfood=False maybe)`.
But region_food checks turn terminal no.
Detailed score region.

`region_food` accepts cap and max_food_dist optional:
For policy health low but don't need food maybe return.
Use same.
Could be expensive.

Region function:
```
if sid missing return 0,None
blocked=board_block(st)
start...
seen...
foodmask...
limit=max(0,min(s.health-1,120))
found=None
dist=1
while q:
...
 if food: found=dist
...
 if found is not None and count>=cap: break
 if dist>limit and found is None and count>=cap:
   # no need search farther than health
   break
```
If no found beyond health, return None (food not reachable in time), even if farther. Good.
But if count cap reached before food and dist <=limit continue.
If health=100 limit99.
`maxdist=min(health-1, 100)`.
If food farther, irrelevant.
For enemy region no need find, can pass `want_food=False`, stops at cap.
```
if not want_food and count>=cap break
```
Own evaluation wants.

Food under head none.
If queue exhaust.
Count can exceed cap but return cap.

Board block all snakes mode0.

Evaluation key:
`EVAL_CACHE[st]`, state nested.
Find own.
No enemies.
Max turn.
`wantfood=True`.
eregion with want false.

Food spawn could put under? no.

`region_score` cap:
```
if NUM_START? current snakes
cap = min(AREA-1, max(60, length*3))
if n snakes >2 cap=min(cap,160)
```
For length 3 cap60.
Flood count count excludes head, max area-#bodies.
Score cap*3.

Threshold:
```
if count < length: -8000 -(length-count)*120
elif count < length+4: -2500 - ...
elif count < length*2: -500
```
A snake length100, region110 on 15 board gets -2500 despite maybe enough. Fine.

Food:
`fdist None`: -10000 - health*20 (if high worse) + tail proximity.
If fdist>=health: -6000 -...
Else score.
If health<20 and fdist >2 - (20-health)*30*fdist maybe.

Could make no food penalty not exceed death terminal but enough.

Enemy region:
```
ecap...
eregion=...
space_diff= min(count,cap)-min(eregion,ecap)
base += space_diff*2
```
If enemy region small positive.
If `eregion < elen`: +5000+...
If own length >:
distance approach.
Else avoid.

Brawl no enemy regions.

Mobility:
`len(valid_actions(st,own))`; can be expensive mask cache but okay.
Note valid ignores enemies, not actual.
+35 each.

Tail fallback:
`td=manhattan(head,body[-1]); if no food base -=td*8`; tail adjacent can score less.

Food length reward.

`MAXT` global.

Quick score uses board block.
Nearest food manhattan.
`risk_good`.

Root risk:
Own new head; own ate maybe.
For each enemy action:
```
if nbit & mask_body(e.body, 1 if eate else0): bad +=2
if enh==ownh:
 if len(enb)>=len(onb): bad +=4
 else: good+=1
```
Could enemy action invalid dynamic other body but valid self; okay.
`onb` for length; if own ate grows.
If own head in enemy segment, bad regardless head.
If enemy destination same and own longer, no bad.
Risk category could count 10 enemies and min.

Enemy valid action calls valid_actions; if no valid returns doomed current possibly; risk.

Fallback quick:
```
base 0
if dest food +500
-nearest*15
open neighbors not blocked *25
-riskbad*10000 + riskgood*300
+ region? no
```
Cands already minbad but include risk anyway.
If own current dir +3.

Search functions:
`is_terminal`.
`own_missing`.

`eval_terminal`: in evaluate.

Duel root:
```
def duel_values(cands, depth):
 enemy...
 eacts=valid_actions(root,eid) # all
 eacts order policy? policy_actions top len maybe detailed.
```
To preserve all, get scored all `policy_actions(...,4,True)` returns top4. If valid >4 impossible dedup max4.
for own:
 worst
 for ea...
 checktime per branch
 ns
 v=eval if depth<=1 else duel_search
 ...
```
Alpha `best`.
If all own candidate maybe.
If any action immediate all.
Return vals.

Recursion enemy `policy_actions(st,eid,4,False)`; returns top4. Own actions quick.
Depth.
At node, alpha beta.
Checktime increments.

Potential valid enemy policy excludes all due other current head collision; valid_actions ignores others, policy may return none. Use valid_actions.
At duel actual adversary might move into our current head and die body, not kill us; no need.
Use policy top4 but if policy filters candidate due other body, okay.
At root use valid all perhaps candidate into our current body dies only, cannot hurt us except head-on no.

`duel_search` uses policy_actions top4 simple. Policy danger etc.

Brawl:
`plan_cache`.
`enemy_plan(st)`: for each policy top1 simple; if none valid.
Root policies separate.
`brawl_search` terminal, fixed moves, loop acts.
Depth.
`brawl_values(root cands, depth)`:
- enemy list
- baseplan best detailed
- For each enemy determine near:
  current head to own head <=9 maybe, or possible reach own dest.
  select up to3 sorted distance.
- detailed alternatives top4 for near (calls cache maybe).
- For each oa, scenarios:
  baseplan
  for near eid:
    for alt in alts[eid][1:3] ...
    include threat action not top3? top4.
- sim each.
- `subvalue`: if depth<=1 eval else brawl_search(ns,depth-1)
- base val and worst.
Return `(2*base+worst)//3`.
Note alternatives same effective dedup.

At depth1, evaluating 4*7=28 BFS okay.
Depth2, each brawl_search loops 4 =>112 sims each next has eval 112; okay maybe.
Depth3 448 eval, too but deadline.

At `brawl_search` enemy policies simple and cache at unique node no reuse mostly.
Could optimize policy top1 simple no BFS.

Checktime inside loops.

Root first turn maxd4, later3.

Use completed values:
```
vals=quick
for d...
 new=...
 vals=new
 CANDIDATE_ORDER=sort...
```
For duel root function itself uses sorted.
At timeout break.

If custom timeout thrown in outer and caught inside loop only:
```
try: new=...
except SearchTimeout: break
```
Then after loop best.
Any other exception outer fallback, but could hide strategy bug; code should no.

After iterative, add risk good:
`finalscore=vals[a]+good*150`.
Quick already includes. Double but okay.
Choose max.
Tie choose earlier quick order. `max(cands,key=(...))`.

Set `DIRS[you] = best`.

Could randomize if exact tie with hash:
key `(score, -quick rank?)`. max first based cands order from quick sorted. Fine.

Emergency:
Parse width height own body.
current DIRS.
Try dirs effective? Need local effective to avoid reverse.
For each:
- if neck distinct and dest==neck and cur: d=cur, but return d.
- wall/self mode cannot use global cache if W setup maybe; simple tuple.
- score open neighbors using all bodies old[:-1].
- food +.
Return.
If none current if in bounds else first in bounds else up.
Set DIRS.

Potential `decide` catches exception but then emergency may use stale NEIGH mismatched; simple independent.

Now think about self-check time. 12 games, module load under1 sec (code compile fine). First turn depth maybe 7 with 0.75; likely returns before. Later 0.038. `time.process_time` includes decide only. Good.

Could actual CPU slower and policy overhead before search leaves little. Deadline set at decide start; quick always. Iteration checks. If timeout thrown inside first root, caught and returns quick. If timeout not checked during root policy BFS, could exceed by perhaps <10ms. On slow maybe. Add time checks in detailed policy? Policy doesn't know deadline but global. `region_food` can check every? Could call `check_time` in policy loops every candidate if global NODES. But quick/fallback stage shouldn't throw before vals? It is after. Root policies only during iteration. We can increment/check in policy detailed:
```
if detailed: check_time()
```
If thrown caught iteration. Good.
BFS max 961 fine.

Set deadline 0.036 maybe ensure. First turn .75.
Policy/eval before first iteration? quick no BFS. risk O. Then d1.
Use 0.038.

`check_time` uses global DEADLINE. If deadline 0 and called? only after set.

NODES increment in check itself:
```
global NODES
NODES +=1
if NODES & 127 ==0...
```
Call frequent.

Evaluation can be expensive one node but no check until after. fine.

Potential pathological BFS each eval 2*225 and branch 100 =>50k, okay.

Now exact ranking and score:
Survival terminal -9m, trap penalty maybe -20k, so search may choose a move that dies immediately if it avoids being "trapped"? No, death -9m far worse. Good.
Win 9m.
Length 75, food route.

Enemy region + can motivate.

Head-on kill gives win immediate, search chooses.

If own candidate enters food and enemy same, both eat, group if heads same also head collision! Rule two heads reach same food, both count eat then elimination head-head based new lengths. Our sim exact.

Strictly longer by1 survives.

Potential initial overlapping body and head-head length growth.

Let's consider reverse invalid for enemy current direction inference:
State body history can infer actual. If enemy tries reverse, head continues current. We infer current head movement and store. Good.
At state body duplicate neck maybe reverse could be allowed; our effective uses coords.

Food spawn random actual may affect search but acceptable.

Could avoid consuming `random`; we don't import.

Let's perhaps use `time.process_time_ns`? process_time okay.

No file operations.

Need final code only one python block then <=300 Chinese strategy. Ensure no extra code blocks.

Before final, let's simulate code syntax carefully.

Let's draft full.

Potential global declaration in functions.

`body_mask` cache key `(mode, body)`: tuple hash. Cache clear.
```
if len(BODY_MASKS)>50000: BODY_MASKS.clear()
```
Could clear during search and lose but okay.
Mode names:
0 = positions 0:len-1 (head..second-last, next-turn guaranteed)
1 = all
2 = 1:len (non-head)
Loop:
```
end=len(body)-1 if mode==0 else len(body)
start=1 if mode==2 else 0
```
For mode0 len1 end0 no cells; min3.
Mode1 end len.
Mode2 start1 end len.

`board_block`:
```
m=0
for s: m |= body_mask(s[1],0)
```

`shift_body` uses foodset.
If ate append oldtail.

`valid_actions` fallback:
```
if out return
for a:
 d=effective
 if inbounds: return [d]
return [cur or "up"]
```
This may return reverse effective current.
No need avoid self.

`policy_actions`:
Cache key with detailed bool. `st` includes directions.
Check time inside only if detailed.
valid candidates perhaps:
```
for a:
 d=effective
 ...
 if nbit & body_mask(body,0): continue
 if nbit & othermask: continue
```
This othermask means policy never follows another snake's head? Other head old becomes neck, correct death.
Could a snake swap heads? A dest old B head, B's new body neck oldhead => A dies. yes.
Open count:
`for nbid in NEIGH[cell_id(nh)]: if not bit & blocked`.
blocked includes own old no-tail and other; after moving own old head becomes body (mode0 includes), correct.
Score nearest:
```
remfoods=[f for f in foods if f != nh]
```
If ate.
No path obstacles.
Aggression.
Current +6.
Detailed:
`tmp snake health = 99 if not ate else100`
Food remove.
`region,_=region_food(... cap45, want_food=False)`
score.
Cache sorted tuple.

`region_food` uses food mask all. For policy tmp no food eaten.

`evaluate` uses `len(own[1])`.
Food limit if health=1 no layers? region still count. BFS loop; found food dist1 but health limit0. We may still find and then fd>=health penalty. `maxdist=0`, but while traverses count; check `if found and...`; should not stop early due dist>limit unless count cap. Need still region count. If no cap and found, okay. If no found and count cap stops. If count below cap, BFS all. Fine.
Stop condition:
```
if found is not None and count>=cap: break
if found is None and wantfood and dist>maxdist and count>=cap: break
```
So if no found and count cap stops.
If food beyond health but count cap reached, returns None, okay.
If count never cap, finds beyond health, returns dist (penalty).
Fine.

Evaluation terminal at turn:
- If own dead first.
- if no enemies win.
- if st.turn > MAXT or >=? At decide state turn max, before move. Simulation next turn max+1. So `if turn > MAXT`. If state exactly MAXT evaluation shouldn't terminal because a move remains. In search only evaluate after move. Could use `if st[0] > MAXT`. But if search depth0 at raw decide turn==MAXT not directly evaluate except maybe root immediate after sim. So use >.
Could `turn >= MAXT` if convention max rounds state next has max+1. Use >.
Terminal helper same.
If max_turns reached after move, turn=max+1.

Max score:
```
best_enemy=max lengths
base=6000000 + (len-best)*100000 + len*1000 + health
```
If multiple alive, length comparison. Could be less than win but > normal.

Win score uses turn:
`9000000 - min(turn,MAXT)*1000`, later win slightly less. At turn800, 8.2m.
Death -9m+turn*1000 = -8.2m late. Clear.

Normal score maybe up to region 600 + length potentially 961*75=72k, less terminal.
Trap - etc.

Late extra up to 500*len? max.
```
if left<20: base += len*(20-left)*30
```
up to570k if length960, still below terminal but ranking.
Maybe length secondary within survival; good.

Enemy region BFS uses enemy health but want false.
`region_food(... want_food=False)`.

`enemy distance`.
Own longer condition strictly.
Duel score difference.

Brawl food safe.

`valid_actions` mobility includes self only; if no,0.

Root quick open uses `NEIGH`.

`quick_score` needs risk args.

`root_risks`: own move:
- We know action valid self, but if dest food own body shift.
- enemy action valid self only. Use `valid_actions`.
Potential valid_actions fallback returns direction out if all out? fallback picks inbounds; if none current out. shift.
- enemy `enh` wall: skip risks (no collision).
- mask mode =1 if eate else0.
- Head compare.
If own dest outside (not valid) no.
Return.

`policy_actions` could filter all due other blocks; fallback valid_actions.

`root_duel_values` enemy acts from `policy_actions(...,4,True)` but policy filters moves into own current head/body which would only kill enemy and cannot hurt us except if destination equal own destination? Example enemy head and own head choose same cell that is also own current body? Own destination can't be own current body due valid self except tail; enemy head dest our current tail could eat? If enemy moves into our current tail, our tail vacates; safe unless we eat. Policy other block excludes our no-tail, so enemy doesn't consider following our tail. This could be a head? not head-on. Doesn't hurt.
All relevant enemy actions likely.
But adversary head-on candidate into own destination is not current own body (unless own loops), policy allows unless danger; included top4 all four. top4 exhaustive.
If policy returns 4.
Root valid candidates max4, so exhaustive even if policy filter? It may filter some. Could just use `valid_actions` to guarantee. Order via policy. Construct:
```
ordered=policy
for a in valid if not in ordered append
```
Do.
Recursion same perhaps policy exhaustive max4 but filtered. Add valid.

`duel_search` branch 16.

Move ordering own root cands from quick.

`duel_values` calls `check_time` per.
If depth1, evaluate.
At alpha, worst can be -9m.

`duel_search` own actions sorted by `state_action_quick`.
Enemy actions policy.
No root ordering.

Brawl root plan:
```
base = enemy_plan_detailed(root)
```
Could simply dict.
Near alternatives policy detailed each near. This duplicates policy call for base top1. Cache keyed topn differs.
Fine.
Scenario per own action plans copies dict (10 entries) 6*4.

Could optimize base tuple of (id,action), variant dict.
`plan_base` dict.
At each:
 `scenario_moves=dict(plan_base); scenario_moves[you]=oa`.
For variant update.
`next_state` loops actions dict get, okay.

`brawl_values` calls check each scenario.
Subvalue.

`brawl_search` fixed moves:
```
em=enemy_plan(st)
acts=valid_actions own sorted
for oa:
 moves=dict(em); moves[you]=oa
```
dict copies.

`state_action_quick`.

`enemy_plan` cache key st; no snakes count maybe.

`decide` global cache clearing:
```
EVAL_CACHE.clear(); POLICY_CACHE.clear(); PLAN_CACHE.clear()
```
Body masks persists.
Set `FOODSET` no global.

Deadline:
```
budget=.78 if raw["turn"]<=1 else .038
```
First turn initial detailed and deep maybe. 1 sec allowed, use .82. Use .78.
Later .039.

`turn` maybe starts 1 as says.

Quick candidate selection minbad:
What if risk bad only potential but safe move much lower food. survival yes.

If values from search for cands. `vals` initialized all cands.
At each iteration returns all.
Final.

Emergency direction:
Need avoid using `DIRS` if own id raw.
```
for a...
 if neck distinct and dest==neck and cur: d=cur
...
self_block = set(body[:-1])
blocked=set for all bodies[:-1]
```
After move current heads become body, so open count blocked includes.
Food.
Return best.

Potential global `LAST_HEADS` update before exception then emergency sets dir. okay.

Let's consider code catching `SearchTimeout` inside `_decide`, not outer. `check_time` may throw in `policy_actions` during root iteration and caught around call.
Set old vals.

At first iteration root duel policy detailed uses check; if timeout, no new. quick.

Detailed policy call from `duel_values` occurs inside try.

Brawl `brawl_values` root alternatives inside try.

No timeouts in quick.

Search node count global persists but only deadline.

Now improve evaluation of immediate safety with enemy action fixed at brawl. Root risk.

Potential issue scenario combination uses `base` action for far enemies but policy may be bad. okay.

Could include aggressive alternative for enemy based all valid action that threatens own destination:
When selecting alternatives for near:
```
pol = policy_actions top4
alts=pol[1:]
for a in valid:
  enh...
  if enh==own_dest or own_dest in post body and a not alts: alts.append
```
Post body check.
Max3.
This catches suicidal attack.
Implement inside brawl_values for each oa, since destination differs. Could precompute valid enemy all and policies.
For near eid:
 `alts=list(pols[1:])`
 for va in valid_actions:
   if va not...
   enh,enb,eat
   if enh==dest or dest bit & enemy post mask: append; break
Then scenarios up to maybe 1+3*3=10.

Good.

Enemy policy detailed alternatives may include candidate whose destination own dest and own longer; if own survives, not threat. But okay.

Root risk already.

At brawl scenario combining alt only one enemy, not coordinated. reasonable.

Potential enemy top policy at future avoids our head if shorter; search.

Let's think through multi-snake head collision ranking:
If 3 heads same and lengths 5,5,4 all die. next_state.
If lengths 5,4,4 5 survives.
Even if 5 starved same turn, group says 5 survives headhead then starved dead, 4s also dead. Our mark group all others, strict winner already dead. yes.

Collision with body:
Segments from snakes that will die included; conservative. likely.

Food respawn after dead removal exact.

Timeout behavior if no response judge straight; our return.

Now possible self-check expects no annotations? Standard.

Let's write final code and then strategy summary <=300 Chinese characters. Need count around 180 Chinese chars.

Before final, let's inspect code for undefined variables:
- BY_DELTA
- YOU etc.

Let's formulate.

Detailed code:

```
def cell_id(p):
 return p[1]*W+p[0]
```

Default dir.

`make_state` raw:
```
snakes.append((int..., tuple(body), int health, DIRS.get(id)))
```
`length` raw may mismatch body due bugs; use body.
Food tuples sorted.

Direction update delta:
```
delta=(head[0]-old[0],...)
```
If invalid maybe keep.

`LAST_HEADS` only alive.

Evaluation cache key st; if cache grows maybe clear each call.

`TERMINAL` constants.

`evaluate` food list.

Enemy region call:
```
eregion,_=region_food(st,en[0],ecap,False)
```
Signature return.

Brawl max number alive can drop, perhaps when 2 remains use duel search! Decision currently chooses mode based raw num alive maybe if len snakes==2. Use `if len(root[1]) == 2: duel` regardless initial. This improves endgame. `state["num_snakes"]` initial irrelevant. In decide mode `len(st[1])==2`. Good.
Evaluation also detects len enemies==1.
Brawl search when snakes reduce to2 still uses deterministic enemy one plan; could switch in `brawl_search` to `duel_search` if 2. Add:
```
if len(st[1])==2: return duel_search(st, depth,...)
```
In brawl_values sub after first move maybe if enemy died and 2, recursion brawl_search switches. If no enemies eval.
Mode root.

At root duel candidate enemy all.

Policy center uses W/H.

Potential number alive >2 but raw duel impossible.

Evaluation cap if len snakes>2.

`MAXT` set.

Check `default_dir` for head center tie.
```
if x < W//2 right elif x>=... left ...
```
At center, choose up/down based y.

`plan_cache` key state, stores dict; return copy? brawl_search modifies copy after. root stores base then variants copies. Safe.

`policy_actions` cache returns tuple.

`region_food`: food bit set.
If food found distance but count cap maybe.
`maxdist=max(0,min(health-1,120))`.
If no foods, found none.

BFS `count` increments all accessible cells; if cap reached but want food and dist<=limit continues. It will count beyond cap? code:
```
if count<cap: count +=1
```
No count beyond. Stop as above.
If found and count cap after adding, break.
If found before cap, continue count.
Good.
If no food and cap reached, break if dist>limit? If dist maybe <= but cap enough region, no need exact food beyond health. Break as soon cap regardless:
```
if count>=cap and (found is not None or not want_food or dist>maxdist): break
```
If found none and dist<=limit continue.
If health high.
Return min(count,cap), found.

Detailed policy calls want_food False stops cap.

Evaluation own food path.

`enemy_plan` policy simple may checktime? `check_time` at search node.

Policy detailed check at each action can consume node count.

`state_action_quick`: valid actions already, but can compute:
```
ate nh in foods
score...
for neigh open...
```

`duel_values` uses global root and cands.
```
policy_order = policy_actions...
valid=valid_actions
eacts=policy_order + missing
```
Policy might fallback valid.
At root detailed, policy_actions check time.

When depth >1 call `duel_search(ns, depth-1,best,INF)` alpha best. In recursion alpha-beta:
```
for oa:
 worst
 for ea:
  v
  if worst <= alpha: break
 best...
 alpha...
```
Pass alpha into recursive? At root for branch enemy min, can pass alpha=best beta=INF. At recursion own max uses.
Within enemy loop, once worst<=alpha prune.
No beta meaningful but pass.
In recursive:
`v=duel_search(ns, depth-1, alpha, beta)`
After each own, alpha=max.
No min player beta update because simultaneous worst local. Correct enough.

Could use beta to prune own if worst? no.
Depth terminal.

`duel_values` store each worst even if pruned? If pruned because <=best, exact not needed; but returning vals for action might be upper/lower. For next ordering fine. But to consider complete iteration, values for pruned action may be alpha bound not exact, could be higher? Pruned only worst<=best, we set vals[oa]=worst (could be <=best), won't be selected over best. fine.

`brawl_values` depth if ns terminal and depth >, brawl_search handles evaluate.

Near enemies:
```
dists sorted manhattan own head current, <=10; if none nearest 1
```
Up to3.
Detailed policies for near once, but `policy_actions(root,eid,4,True)`.
Base plan detailed top1 all enemies; calling near top4 separately.

Scenarios for each oa:
```
variants=[]
for eid:
 alts=...
 for alt in alts[:3]:
  if alt != base[eid]: variants...
```
Threat detection valid all:
```
for va in valid_actions(root,eid):
...
 if enh==dest or bit & mask...
```
Post enemy body segment mask mode ate? mode1/0.
If own dest in ebody[1:]. If own dest equals enemy head, head; else body.
Add.
Need if va is current direction etc.
Avoid duplicate.

Scenarios tuple `(eid,alt)`.

`base_moves` each scenario:
```
mv=dict(baseplan); mv[YOU]=oa
```
Base plan includes only enemies, no own.

Combine ints.

`brawl_search` if len==2:
```
eid...
return duel_search(st, depth, -INF, INF)
```
But duel_search perspective global YOU.
Good.

In `_decide`, if mode changes complete.

Risk root in duel also.

Final best if cands maybe.

Now strategy description:
"以严格结算模拟器为核心：精确处理尾缩、进食停尾、饥饿和多头同格；每回合先做所有对手可行动作的风险筛查，再对单挑做同时行动极小极大迭代加深，大乱斗用对手策略预测和近敌变体场景滚动搜索。评估用洪水填充空间、限时食物BFS、饥饿、机动性、长度和敌我区域/头对头关系，超时保留已完成最佳。" Under300.

Need ensure code block only and summary after. Good.

Let's maybe assess whether summary says all.

Before final, potential issue policy detail and deadline custom exception could be caught by `_decide` outer generic if occurs outside iteration. We call no policy before try loop except maybe quick no. okay.

Let's code carefully.

Full code:

```
import time
...
def decide(state):
 try: return _decide(state)
 except Exception:
   try: return _emergency(state)
   except Exception:
      return "up"
```

If `_decide` catches SearchTimeout? It catches around each. Generic outer for bug.
Set direction in emergency.

One concern: Broad exception could make self-check pass but strategy silently fallback if minor state bug. Better than error.

Let's write code mentally and perhaps detect syntax.

Code length maybe 600 lines, desired okay.

Let's optimize root evaluation.

`body_mask` global cache key mode/body. If cache clears during iteration, okay.

`food` raw may list lists. tuple sorted.

`state` max turns default.

No type hints needed (standard).

Now let's write actual final code in analysis draft:

Potential line:
`m |= body_mask(s[1], 0)` where s tuple index1.
`other_mask` policy loops.

Policy detailed `tmp = (st[0], tuple(tmp_snakes), tuple(f for f in st[2] if f != nh))`
Tuple order.
`region_food(tmp, sid, 45, False)`.
No issue if ate health.
Tie score float due center. Return tuple sorted.

Evaluation `fd >= health` if fd integer.
`food_term`.
`taild`.

`MAXT` maybe 0.

Terminal max score could exceed WIN? use 6m.
If own is only survivor, no enemies => win9m.

`late` extra.

Root risk own body shift:
`ohead, onb, oate = shift_body(...)`
If own action valid but destination current enemy etc.

`mask_body(e[1], 1 if eate else 0)`: If enemy ate, post nonhead segments old full. If no, old excluding tail. Correct.
But `e_new_body[1:]`:
- noeat old body[:-1]
- eat old body all.
yes.
Mode0 includes old head..secondlast.
Mode1 all.
If own head is old enemy tail and enemy eats at another destination, mode1 catches.
If own head is old enemy tail and no eat, safe mode0 excludes.

Policy other mode0 underestimates tail stays if enemy eats; okay.

Next collision `body_mask(nb,2)`:
- noeat nb nonhead old excluding tail
- eat nb nonhead old excluding tail + old tail (old all)
exact.

Spawn occupancy mode1 includes all.

Emergency self check body[:-1].

One subtle rule: Snake that ate last turn tail does not move next because duplicate tail representation, our general move pops one tail and duplicate remains. mode0 body[:-1] blocks duplicate due first instance. correct.

`region_food` blocked excludes body[-1] but duplicates remain.

Now check `valid_actions` current direction reverse:
`effective_dir` if action destination==neck. At start body[1] same head, no directional destination equal same, no.
If body [head, neck] distinct.
Dedup set.

`state_action_quick` no risk.

`duel_search` policy top4 simple. Policy may return less due filter; append valid all:
```
p=...
va=...
for a in va if not p append
```
Thus exhaustive, policy only ordering. At every node enemy all non-self-death. Branch 16.

Time depth5 worst 1m, deadline.

Root values cands sorted by vals before each iteration:
```
CANDIDATE_ORDER = sorted(CANDIDATES,key=lambda a: vals.get(a,...),reverse=True)
```
Global used? `duel_values` uses CANDIDATE_ORDER.
Quick vals.
At depth complete update.

`brawl_values` also.

Global declaration `_decide` for many:
```
global START,DEADLINE,NODES,ROOT,YOU,W,H,MAXT,AREA,CANDIDATE_ORDER
```
`setup_board` sets.
No need declare if not assign? _decide assigns ROOT etc yes.

`infer_directions` assigns LAST_HEADS, not W.
`setup_board` declares.

In `_decide`, call `setup_board` before infer so default.

Caches globals assigned clear no declaration? Mutating no.
`ROOT=...

If broad exception before DIRS best, emergency.

`FINAL` no.

Let's maybe include `time_left` turn.

Now likely good.

But let's question if 50ms budget includes CPU time across process cumulative? "每回合50毫秒" likely per call. time.process_time resets no, but deadline uses difference from start call, yes.

First call module global direction none and turn1 .78 sec. Search can use. Subsequent process_time absolute increasing, deadline absolute `start+0.038`, okay.

Potential recursion SearchTimeout thrown while inside after deadline, caught loop, then outer returns quick almost immediately. No repeated check during final max.

Now possible judge counts exceptions if decide catches internally no.

Let's perhaps not catch SearchTimeout in outer generic prematurely.

Now refine evaluation for enemy policy prediction:
Policy score detailed uses region and center. Baseline "avoid immediate death, look space, chase nearest food". matches.
Strong opponents could trap, all candidates in duel minimax.

Brawl fixed policy.

What if own enemy direction unknown at turn1; policy current no momentum. all.

Now collision risk root considers enemy actions that are self-valid but maybe action reverse maps, yes.

Potential action risk counts own destination in enemy body after enemy action even if enemy dies from self? valid self prevents self, could die other. Conservative.

Space region flood starts after root but does not model our next move; search.

No explicit route reservation but okay.

Let's estimate code performance with body mask caching:
Policy `body_mask` hash tuple body each call. Fine.
Flood board block hashes all bodies each eval. Cache.
`state` hash includes body; eval cache.
Brawl recursive every node enemy policy: for each enemy 4 actions; other_mask loops 10 and body masks cached. ~40*10 bit checks. At 400 nodes 160k okay maybe 20ms. Deadline.

`enemy_plan` plan cache key st hashed; at each node.

Brawl depth3 root scenarios huge; may only complete d2. d2 robust.

Duel policy each node enemy all; good.

Could dynamic depth based turn/lateness:
Later snake lengths body masks longer but cache unique next states. 50ms. Max depth maybe 4 duel, brawl2. But iterative starts d1,d2, then attempts. fine.
Maxd 5.

First turn can d7.

Now maybe add if health low reduce depth to make decision timely? Search finds food.

Now write final answer. But before, let's mentally lint each planned function in actual code.

I'll construct in final carefully.

Potential use of variable `foodset` in `next_state` and `remaining`:
```
eaten=set()
...
if ate: eaten.add(nh)
remaining=[f for f in foods if f not in eaten]
foodset=set(remaining)
```
Good.
A food could be tuple outside no.

Head groups key integer. Store rec list.
Dead IDs set.
Survivor tuple direction effective d (even if grew).
Moved rec maybe dictionary.
```
records.append((sid,nb,nh,h,ate,out,starved,d))
```
Indices.
Wall mark `nh[0]<0`.
Body collision head bit.
Head group all records including starved/bodydead.
Strict winner based len(nb), includes growth.
Dead survivor check.

No concern tuple IDs duplicate.

Policy tmp health:
`nhlim = s[2]-1`; if ate=100.
No starvation filter; candidate at health1 with food should actually die before eating, policy should filter. valid candidate could be lethal. Add:
```
newh=s[2]-1
if newh<=0: continue  # even if ate, dies before eat
```
Important. `valid_actions` doesn't account starvation. For own, at health1 all moves die even if adjacent food due hunger before eat, unless health? Rule health decrements then food, so no action saves. Search sim. Policy enemies should consider. Add in policy if s health<=1: valid action still sim death, but prediction irrelevant. Could return valid.
For own valid at health1, all die; risk fallback. Fine.
Policy candidate:
`post_health=s[2]-1`; if <=0 score -1m perhaps not filter (all same).
If ate reset but dead. score low.
Detailed region not useful. Return.

Policy ate only if health>1.

`shift_body` growth even if starving, next_state marks.
No issue.

Evaluation if health <=0 shouldn't state alive.

Food distance path requires health>dist.

Policy nearest foods after eaten:
```
fs=st[2]
if ate: fs=tuple(..., but generator)
```
Membership tuple.
Use `foods_after`.

Open count blocked uses current board block; if destination's cell itself not in blocked, neighbors.

Detailed region state includes other old heads as blocked mode0, models their neck. Good.

Policy danger candidate head-on:
Other head can move into nh if adjacent but could be blocked by its own reverse; any adjacent direction potentially effective except reverse. We ignore.
Compare lengths after candidate ate and other maybe current. Use `my_len=len(nb)`.
If o length >= my_len - etc.
Also distance chase.

Current direction bonus.

`region_food` no global check.

Quick score food at destination even health1; no.

Root risk if own health1 all die, candidate all, final any. okay.

`evaluate` if health low.

Max turns raw state.

Let's maybe add `state["num_snakes"]` unused.

Now final code can be long. Ensure summary after code not within.

Let's compose final.