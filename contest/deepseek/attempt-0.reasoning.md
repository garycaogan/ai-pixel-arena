We need answer with code block and brief strategy <=300 Chinese chars likely. Need craft strongest snake AI in Python stdlib, time 50ms per turn, 500/800 turns, up to 31x31 11 snakes. Need robust no timeouts. Need code only + description? User says reply only one python code block, after code description <=300. Need final include code block and short text. Need design.

We need implement bot.decide(state). Need strong amidst multi snakes. Need consider simultaneous moves, collisions, body, tail, heads, food, space. Need efficient. 15x15 or 31x31. 50ms. We can implement heuristic with search/rollout maybe limited. Need account for venom/head collision length. We can inspect current state only, cannot know others intentions. Need decide.

Strategy ideas:
- Safe immediate move: avoid walls, bodies excluding tails that will move; account for heads contest; avoid moves into potential head-on if opponent could enter and length >= ours.
- Use local search (beam/Monte Carlo) to evaluate moves with future safety, food, space, aggression.
- For small duel, stronger.
- Multi, prioritize survival, avoid being trapped, length.

Need produce code robust within 50ms. Python 3.13. Up to 31x31 board 961 cells, 11 snakes. 50ms ~ maybe 1e6 ops. Need efficient.

We can implement:
1. Collect obstacles. Determine occupancy set of all body segments except maybe tails that will move unless snake length=1 or tail condition? Actually static predict next move occupancy after first movement before eat? We need evaluate candidate head positions and compare.
2. For each possible direction, simulate our move? We only need head target. Determine if immediate lethal:
   - out of board.
   - target in any current body segment that remains after moves. For any snake, its tail will move unless snake length==? If body has duplicated tail means just ate prev turn -> next tail doesn't move? Example if last two overlap, after eating last turn, next turn tail won't move? Let's understand: Eating occurs end of turn, body grows by adding new section at tail, so for next turn tail does not move (because added "tail" segment maybe duplicate old tail; first movement tail shrinks? If body includes duplicate last two, at next step tail shrinks one cell, removing one duplicate -> tail effectively stayed. In current state at turn start with duplicated tail, during movement step tail simultaneously缩回一格. If duplicate, after shrinking, one copy removed, current tail coordinate remains as body? Let's simulate body [head,..., tailcopy, tailcopy]. Move: tail shrinks; remove last segment (one duplicate), so one tail duplicate remains. Thus current tail cell still occupied. So if last two equal, tail doesn't vacate. Need exclude tail only if it will vacate (last!=second last and length>1). Also if grow? Body current represents before movement. Eating happens after move; can't know until head target has food. For collision with tail, current tail if will move vacates. If next head target is current tail and tail moves, safe even if our length? If our head enters where tail was after shrink: yes.
   - head-on contest: target in opponent's possible next head cells? Actually simultaneous. Need know if multiple heads choose same target. Could avoid target occupied by other head? Current head cells vacate if they move but if they stay? S movement always direction; can't stay. If our target equals current opponent head? It will move, so could be safe after shrink, but if swap collisions? Rule head撞到 body (not head?) In move, heads move simultaneously then eliminations: "头撞到任何一条蛇的身体（除蛇头以外的任意一节，包括自己的）"; heads not body? Head-to-head evaluated same cell. If we enter opponent's previous head cell while it moves away, maybe safe. But head-on simultaneous if both enter same cell; we can't predict.
   - We can model danger from other snake current head possible directions. To avoid head-to-head death: if our target is reachable by an opponent on next move, and opponent length >= our length, then risky. If our length > theirs, we'd win if they move there? Actually two or more heads same cell: longest survives, others die; if tie all die. If we are longer, we survive even if tie with shorter? "最长的那条活下来，其余死；一样长就都死" If multiple, max length survives? If two longest tie, all max die maybe. If we strictly longest, we live, others die. So we can intentionally contest shorter. But other may avoid.
   - Need also if opponent can choose target, not deterministic. In heuristic, penalize cells adjacent to opponent head when not longer, esp if closer.
3. Evaluate future space: Flood fill accessible area from target using obstacles after simulating moves (tail vacates). Could be expensive for each move but board small. Evaluate area, distance to food, length, health, centrality, risk.

For 50ms, maybe do beam search with deterministic simulated others? But others' moves unknown. Could use minimax? Single player search assuming others continue current? Need robust.

Since opponents are other AIs, need competitive. We can implement Monte Carlo/beam searching our future assuming passive environment and predicted opponents? The actual game has simultaneous hidden decisions each turn but at each decide we see current positions. We can simulate our snake and approximate other snakes using simple movement? Hard.

We can develop strong heuristic:
- Generate our safe candidate moves via immediate collision, head risk.
- For each, evaluate:
  - survival area (flood fill) with all current bodies adjusted for one step? To be safe, use conservative obstacles = all current bodies (including tails) except our own tail maybe plus walls, then compute reachable cells from candidate assuming all snakes bodies static. But tails will move perhaps; using current bodies may underestimate.
  - territory relative to opponents: accessible region not cut off by opponents.
  - shortest path to food, considering obstacles and maybe dangerous.
  - health urgency.
  - aggressive head collisions: can kill shorter? But risky.
  - avoid moves that reduce mobility options (degree etc).
- Use 1-2 ply: For candidate, simulate our body after move; for opponents could consider all possible moves? Maybe approximate "potential head collision occupancy in 1 step"; recompute new danger.
- For survival in long term, beam search our own snake with static/optimized environment? Could search paths to food avoiding static obstacles. But moving obstacles matter.

Given only one reply no test. Need robust code with no syntax errors. Let's design carefully.

Potential strategy variant: Trap avoidance using flood fill and tail-follow. In multi up to 11 snakes, early game long random.

Time management: num_snakes small? Use a simple fast implementation.

State parsing:
width=state["width"], height=...
snakes=state["snakes"], me find by id.
my_body list of [x,y]. Directions tuples dx dy.
Current occupancy by coordinate. Build dict coord->snake id maybe with segments and segment index. We need tail moving info per snake: body length (given length may equal len body? body can have duplicates, length maybe number of segments length same as len(body) perhaps duplicates count; state example length=4, body has 4. Use len(body) for collision shape, length for contest? "length" likely sum segments including duplicates. Use len(snakes[k]["body"]) or given length. Use length for head collision, body occupancy actual list all segments.
For each snake, determine tail_vacate: len(body)>1 and body[-1] != body[-2]? At movement step, if tail unique, remove last. If duplicate, after shrink still occupies same coordinate. More generally if body last != body[-2], tail coordinate vacates by next move unless snake eats? Tail shrinks before eating, and if it eats it adds a segment at tail after head move, which may refill? Rule order: move, health, eat. When eating, body grows by adding new section at tail. Does the tail that shrank during move get restored in same turn if grows? They said "新的一节加在尾巴上，所以吃到后的下一回合尾巴不动" Means at eat, add to tail after move; current tail? Let's simulate normal body [H, B, T]. Movement moves head, remove T. If eat, add new section at tail. The new tail likely duplicates new tail? Wait typical snake growth after eating: body list after move [newH, H, B] then add at tail? Existing tail is B; "new section added at tail" could append B? In example state after eating previous turn has last two same [9,5],[9,5]. Suppose before eat length 3 [9,3],[9,4],[9,5]. Move to [9,3]? Hard.
At current state last two duplicate means it just ate, so next movement tail does not move. Thus if last two duplicate, current tail cell remains after shrink yes. If eat this turn, additional duplicate at new tail after movement, affecting next turn. For immediate collision, our head entering current tail of another snake: if its tail will move, safe; if it will eat this turn, tail might not vacate? But tail moves first before eat; if it eats, new tail added at coordinate of old tail after shrink? Let's derive. Suppose before move body [H,A,T]. Tail not duplicate. Movement: head H->H', tail T removed. Body [H', H,A]. If this snake eats at H', add new tail at tail end? "新的一节加在尾巴上" likely append A? Then body [H',H,A,A] (last two duplicate). Thus the old T vacated regardless; growth duplicates A, not T. So current tail vacates if unique even if snake eats. Good.
Thus collision target being current tail of any snake safe if unique tail (and not our body?) because tail removed. If duplicate tail, remains.

But when checking candidate target, need account that head moves and tail removed simultaneously. Our own current tail vacates if unique. If our candidate equals our own tail and unique, safe (self-follow). If our candidate equals another snake's unique tail, safe even if otherwise body. If target equals head of any snake? Heads are not "body excluding head"; after movement current head vacates. If it moves into same target? contest. If it moves elsewhere, safe. So current head cells are not obstacles for body collision. However if an opponent is length? It vacates always. We should treat current heads as free for body collision except head-on potential. Rule says head撞到 body excluding head. If we move into current head cell after it moves away, safe. If opponent chooses same target, head-on. We can't know. So immediate body obstacles should exclude current heads? Wait if we move into cell currently occupied by opponent head and opponent also decides direction away, safe. If opponent decides direction into ours? head-on. For self current head? Our next head target not own current head unless reverse? Reverse invalid. Body excluding head.

Important: When checking target in own body, exclude body[0] and unique tail if vacate. Also exclude duplicate? Occupancy after move includes own body excluding moved head and removed unique tail. If target is body segment that will still be there, death. If target is own current head? Not possible except reverse? Actually reverse direction ignored by rule, but we choose directions; if choose opposite current direction, move uses original direction (not reverse). Need know current direction? State doesn't directly give direction except body[0] and body[1]. If body has duplicates at start, can infer? My body [9,3],[9,4] head 9,3; current direction likely from previous movement from neck to head = (0,-1) up? To not reverse, if choose neck direction, invalid and it will continue original direction. Our decide returns a direction; if invalid reversal, bot still moves original direction, not our selected. Better avoid returning reverse; determine current direction from head - body[1] if distinct; if body[1] same? At spawn length 3 stacked, body[1] same, no direction. Need handle duplicate neck. There may be multiple same at head at spawn. Current direction unknown. Returning any maybe first turns. For safety, our move simulation should know returned direction; if it is reverse of current, actual movement will be original. Need infer current direction from first distinct body segment: find first body[i] != head, direction = head - seg? Actually body[0]=head, body[1]=after head (neck). If duplicate due to spawn/growth, search first distinct in body: vector from body[i] to head? Example snake moving right: head (5,0), neck (4,0), body [5,0],[4,0]; current direction right = head - neck = (1,0). If all same, no dir, any non-zero works. If reversed invalid, actual direction = current direction. Need simulate actual_move for chosen direction: if body[1] distinct and chosen == opposite current, then actual = current. Also if only one length? But length >=3. If duplicates, search distinct; if none current none. If chosen reverse current, actual current.
Important for decision/eval. We return chosen but evaluation must map to actual move. Need use actual for collision. If chosen reverse, might be bad; simply exclude reverse direction except no current. So returned always valid non-reverse. Thus actual=chosen. At spawn no current maybe all body identical; any direction. Direction not known but reverse undefined.
Dir names list maybe [("up",(0,-1)),...]. Need maintain order deterministic maybe.

Head-on risk: Need estimate possible cell opponents may move next. For each opponent, list potential next head cells after considering direction? They cannot reverse according to their current direction (unless no direction). But their choice unknown. We can approximate all four directions? Better determine their current dir and exclude reverse. If body duplicates, all. For each candidate target, if target equals any possible next cell of opponent with length >= our new length? Need decide penalty. If opponent same length and both choose target, both die. We should avoid unless no choice. If opponent shorter, we'd survive if strictly greater. If equal or longer, fatal. But note if multiple? Only same cell.
However if opponent possible next cell but not necessarily chooses it, a small penalty for being within adjacency, because if both choose colliding. But we can calculate minimum distance etc.
In multi, many heads around, head-on risk high. Use penalty large.

Also potential body collision with opponent after their move. Our immediate target current body safe if not tail; but an opponent could move into our target? That's head-head. Or their tail vacates. We ignore their new body occupying target from movement? A snake's body segments follow; a segment at target could be occupied by previous neck if head moves? Wait body after moving: new body = [newhead, oldhead, oldbody[0],..., before tail removed]. Thus current head cell becomes body segment (neck). If our target is an opponent's current head cell, after they move, their old head remains occupied by their new neck, unless that opponent died? Ah! Critical: Body collision after movement: all bodies move simultaneously. Current head cell becomes body (neck) for snake after it moves, and since it's not head, our head colliding into that cell would hit its body! I previously thought vacated, but snake body follows into old head. For our own move, old head remains as neck. So target equal current opponent head after they move is occupied by their neck (unless length? length>=3) regardless of their direction, except if they move and tail shrink length maybe still. Thus head cell is body obstacle for other snakes! Rule says head撞到 any snake's body except head. After movement, old head is no longer head, so body. So yes cannot enter current head of another snake, unless that snake dies this turn? Death simultaneous after collision; but our head would collide with body of living/dying? If opponent dies by wall maybe disappears in elimination after body collision? "死掉的蛇立刻消失" within elimination same step. Collision checks simultaneous. If we enter its old head while it moves out and survives, its old head occupied. If it dies due wall, maybe its body removed, but our head collision with its body maybe simultaneous? Likely if we collide with its body, we die too regardless of its death? Need avoid.
For our own move, target can be our current head? Cannot stay; old head becomes body; reverse invalid. Exclude.
Thus body obstacles after movement are:
For each snake, new body consists of [newhead, old head, old body[0..n-2 excluding old tail if unique? Actually body after movement before eating: [newhead] + old_body[:-1] (if length>1). If last two duplicate, shrinking removes one duplicate: [newhead]+old_body[:-1]. The old body[:-1] includes old head and all except last segment. So occupancy excluding newhead. Current unique tail vacates (not in old_body[:-1]); duplicate second-last remains because old_body[:-1] includes one of duplicates at tail. Good.
For collision with other bodies, we only check our newhead against other snakes' new body excluding their newhead. That includes their current head and old body[:-1].
If multiple snakes' heads same cell, special; bodies maybe after movement too.
Our immediate collision check should check target against old bodies of all snakes excluding unique last segment, and excluding? For another snake, its old head IS occupied after its move as neck; yes include old head. For our own, target cannot be old head due no stay. Include other segments except unique tail. For another whose newhead target also same? handled head-on. But if target is current head of opponent, and opponent moves away, its body moves into current head (neck), so we die by body collision even if not same cell with newhead. However rule elimination order: first, do head-body collision; head-head same cell. Suppose we move into opponent's old head cell; opponent moves away. After movement, opponent's neck at old head. Our head at their old head. We collided with their body; die. Yes. So current head cells of any snake (other than maybe length 1) are deadly.
What about target equal other snake's current tail if it vacates unique: safe if no other. If duplicate remains, deadly.

When evaluating candidate, use post-move body occupancy excluding new heads? For collision, our target cannot be in any other post-move body excluding their newhead? If target equals their newhead, it's head-head. If target equals any body segment after movement including old head and old body[:-1] (and duplicate tail), death. Thus build deadly_body set = for each snake (including us? For us, target cannot be in our current body[:-1] because own new body will occupy own old head and old body[:-1]; but our newhead itself replaces old head? Wait our own new body = [target] + old_body[:-1]. Our target cannot be in old_body[:-1]. If target equals current tail unique, tail excluded safe. If target equals current head impossible (direction zero no). If target equals body segment, death. For own, old_body[:-1] includes current head, neck, etc except tail. Target could be current tail if vacates safe. Include own body[:-1].)
For other snakes, deadly_body set includes all current body segments except if unique tail (then old_body[:-1]); this includes current head. If target in that, we'd collide with their post-move body (even if they die? avoid).
Then head-head: if target also chosen by other snake. We can't know, but their possible newhead cells. If target equals their possible newhead and length contest. Actually if target equals their current head, already deadly body because includes current head. So head-on only same future cell that wasn't current body? Could be.

Need also after step, our own body post-move for future eval.

Immediate legal candidates: target in bounds; target not in deadly_body for any snake after tail exclusion. Wait if target equals another snake's unique tail, safe because not in deadly_body (we exclude tail). If that snake's head also moves into its tail? Could create head-head/body? Its own tail vacates then its new neck etc. If it somehow chases tail with length? Not immediate.
What if target equals another snake's newhead, not in their old body. Then legal body-wise but head-head. Need penalize/avoid. If target in deadly_body current head, we already treat as death, but actually if our target equals opponent current head, and opponent moves away, their old head becomes neck dead. So correct to consider deadly. This means bots cannot move into vacated head. Good.

Now, candidates might all be body-dead except some. If none legal, choose any safe-ish direction with max space? It might die anyway. Need avoid returning invalid. Use fallback direction not reverse and within, but even if body collision maybe death. Since if no legal, choose candidate with least bad (head-on maybe etc).

Direction inference and move map:
Given my body, current_dir = None.
If len>1:
  for i in 1..len-1:
    if body[i] != head: current_dir = (head.x - body[i].x, head.y - body[i].y) sign? If body[i] is neck adjacent, difference adjacent. If duplicate due spawn, first distinct may be two behind but difference larger? Example spawn all [x,y] repeated, then after moves perhaps duplicate? body list maybe [5,0],[5,0],[4,0]? At after growth? The first distinct could be at distance maybe? Current direction is head - first distinct normalized to unit? If duplicates at head due? Example after eating last turn last two duplicate, head and neck distinct. Spawn length 3 all same; no. If head duplicates? Body could have [head, head, neck]? Could happen when just ate? Growth adds at tail not head, so head duplicates at spawn only? Snake body with head same as neck maybe at start. Search first distinct; compute vector from body[i] to head, normalize maybe one step if adjacent or more due all same? If body [5,5],[5,5],[5,5], none. If [5,5],[5,5],[4,5], direction right (1,0), delta 1. Could be >1 if multiple duplicates? Not likely except spawn no distinct. Use sign of dx,dy.
Then if chosen direction is opposite current and current, the actual move will be current. We simply won't choose opposite. If current none, any.

Simulation of our move:
new_head = head + dir.
Our new body before eat = [newhead] + old_body[:-1] (remove last) (assuming not growing yet). But if eat at newhead, after eat append tail duplicate? For future evaluation including food, length grows by 1. However collision with tails affected next turn. For one-step evaluation, should simulate eating and append new tail? Rule: after movement, if food at newhead, health reset, body length +1, new segment at tail. Current body after move before growth = old_body[:-1] preceded newhead (length same). To grow by one, append last element of this body (duplicate tail) to list. So new_body = [newhead] + old_body[:-1] + [old_body[-2]? Wait "加在尾巴上" means append a copy of current tail (last element after shrink) to end. The current tail after shrink is old_body[-2] (since old_body[-1] removed), or if list? So yes body after eat = [newhead] + old_body[:-1] + [old_body[-2]]? Example old [H,A,T], newhead H'; before growth [H',H,A]; append current tail A -> [H',H,A,A] (last two duplicate). Matches example. If old length 1, special. If no eat, [newhead]+old_body[:-1]. But note if current last duplicate, old_body[-1] equals old_body[-2], before growth removes one, current tail old_body[-2] remains; append copy if eat. Good.
Health: after move health-1, if food set 100 else max(0, health-1). Need for decision but this turn only food. Future urgency.

Other snakes movement predictions: For head-on risk and space, we might not simulate them. For candidate evaluation, compute new obstacles maybe with other snakes assumed move forward? But actual unknown. Could build a predicted board for next turn? Since other AIs will move. For survival beyond immediate, need anticipate.

Potential approach: Use "virtual board" for flood-fill from candidate using conservative obstacles: after our move, keep all other snakes bodies unchanged except their tails? But they move. For space, treat current occupied cells as obstacles (except tails/vacated by us). This may be conservative but okay. If opponents move, spaces may open. For avoiding being trapped, need own future.

We can perform beam search for our snake over horizon ~ maybe 6 moves, with static obstacles (current other bodies adjusted along predicted directions? If static, overestimates constraints early but can work). Each state: my body, head, length, health, foods remaining? Use board obstacles from other snakes perhaps fixed plus walls. Search actions non-reverse that don't hit bodies, evaluate reachable area. Max 6 depth, branch <=3, states ~729, each flood fill 961 maybe 700k. Within 50ms? Python 700k okay maybe. But with per turn 800, need efficient. Use horizon 3-5 and optimized.

Better: For each immediate candidate, compute metrics:
- size of flood-fill accessible region from newhead considering all current snake bodies after one step (static obstacles) with tails considered vacated? This estimates space. Large > our length required.
- distance to nearest food via BFS in free cells excluding bodies and dangerous head zones.
- mobility / articulation.
- head danger.

We can also perform a mini rollout: simulate our snake greedily toward food for N steps in static obstacle field; if it can survive and reach, score. But other obstacles static means path through areas that will move. Still helps trapped.

Need handle 31x31 with 11 snakes, many bodies, occupied maybe ~50 cells. Flood fill BFS each candidate 4 times per turn, 961 cells -> 4k per turn *800=3.2M, trivial. Could even do more.

Let's define free cell for our future movement:
- blocked = walls? use bounds.
- blocked by other snakes' current body after considering their tails will move? For future, other snakes move, so not static. But as approximate obstacles, use their bodies excluding unique tail (post one step) maybe plus predicted head? It may change. If treat all current bodies except tails as blocked, my flood fill can overestimate permanent block but okay. Also include our own new body after move except new head? For accessible area from new head, treat our body as blocked (cannot pass through) except tail will move over future. Flood fill with own body static underestimates. Could compute "open cells reachable by head ignoring own body except immediate" to estimate room. Use obstacles = other snakes current bodies (excluding unique tails) + maybe food not obstacle. Own body not included? If not include, overestimates space through self. But snake body moves; head cannot go through current body. For one-step flood, include own body except tail? For room, we care area not occupied by others; own body will follow and can occupy area. Maybe exclude own body for space potential. Simpler: blocked by all other snakes current bodies excluding their tails that will vacate, and walls. Not include own body. This computes open region from candidate. If candidate itself is free, area. Good.

But if target near other head, dangerous. Need compute danger map:
For each opponent, determine possible next head cells. Since they cannot reverse. But for conservative safety, maybe any adjacent cell except wall/body? However current dir inferred. Use possible moves. Define danger_level for each target cell:
  - If an opponent could move there next turn with length >= our new length (tie/longer), high risk.
  - If opponent length < ours, lower (we would kill if contest) but still if multiple? Could be okay.
But because other AIs may avoid, use penalty moderate.

Also body collision after other move: Our target could be current opponent's old head (deadly, excluded), current body except tail (excluded), or current tail unique safe. What about target equals a cell that is not currently occupied but an opponent's body will move into it (e.g., their current head moves into target) => head-head if target is their newhead. If target equals their neck? Current body excluded. If target equals an open cell but an opponent's body following could move into it? Body segments only move to previous segment positions; all occupied positions next are subset current body plus newhead. Open target can only become occupied by a head movement. So head-head covers.

What about our target equals another snake's current food etc.

After one step, our new body may collide with other snake's body? We only check our new head; bodies can overlap? Snakes can overlap? Rule only head collision with body. Bodies of different snakes can overlap? It doesn't explicitly forbid body-body overlap. A body moving into another body? Only head collision matters. So other body-neck can occupy same as our body? It may happen, but not death except heads. Our future head movement must avoid all bodies. Body overlap could complicate. But likely allowed? If two snakes' bodies overlap, they are both occupying cells. Fine.

Need consider if our head target equals any other newhead, contest based on lengths. Our length could grow if food at target. Rule eat after hunger, then eliminations? Actually order: move, hunger, eat, elimination. Head-head collision occurs at elimination after eat? It says after eating then淘汰 simultaneous. So if our target has food and we eat, length increases before head-head comparison? Step 3 Eat food, body grow; Step4 eliminate head collision; So length contest includes growth from food! Important. Two heads same food both count eat and grow, lengths updated then compare. So if candidate target has food, new_length = current length+1 before head contest. For other possible head at target with food, their length may also grow. We don't know if they eat? If same target food, both eat and grow. Compare current+1 for both if they also reach food? If one already at target? Food eaten by all heads there. For predicted head-on at a food cell, both lengths +1. Could help. Need use length_after = my length + (1 if target has food else 0). For opponent potential at target, their length_after = their length + (1 if target has food else 0) because if they move there they eat same food. If target no food no grow. If target equals current food list. Note if two heads same food, both grow. So contest.
If multiple at same cell, max length survive if unique max? Wording "最长的那条活下来，其余的死；一样长就都死" Ambiguous if three with longest two tie, do all die? Likely all tied longest die, shorter die, so no survivor if top tie. If unique longest, it survives and all others die. We'll assume if any opponent length_after >= ours, we die if same target (if equal both die, if longer we die). If all opponents shorter, we survive. If multiple shorter, survive. Good.

Also health starvation: Our health after moving = max(0, health-1), then if eat =100. If health <=1 and no food, die before collision? Hunger in step2 life to 0, eating step3 might restore? Actually hunger decreases, then eat. If health reaches 0 at step2, does snake die immediately? Elimination step4 includes life 0 after eat? Rule order says move, hunger, eat, elimination (life降到0). If health was1, after hunger0, then if head on food, step3 eats and health回满 100, so survives. Thus health zero before eat can be restored. So if target food, okay. If no food and health<=1, die. But state health likely. Include impossible if health<=1 and no food target. In self initial 100, rarely.

Now strategic considerations:
- In single duel, aggressive head-on with longer can kill. If my length > opponent and can move into their possible head cell, maybe kill them. But if they don't contest, no kill. Direct attack: predict their likely food target, intercept. Hard.
- Avoid longer snakes. Eat food to grow and heal.
- In multi, hide, preserve, let others fight.

We can implement candidate scoring with dynamic weights depending num_snakes and turn.

Detailed candidate eval:

Inputs: my snake dict, current dir, legal candidates generated (all 4 dirs maybe excluding reverse). For each dir:
- actual target = head+dir.
- if chosen reverse and current exists, actual=current. To simplify generate only non-reverse plus if current none. But what if only non-reverse moves lead death while reverse would let continue forward also death? Reverse invalid leads forward; we can include the "return reverse" as actual current direction candidate, but returned direction reverse could be okay (it continues). But better if actual current direction not in list? We should consider actual movement directions = all four, but for any chosen that is reverse current, actual=current. We can simply evaluate unique actual moves allowed by rules: current_dir plus all dirs except opposite current? Actually the snake's movement choices: It can turn left/right/straight or choose reverse? Rule: "掉头（走回自己脖子那一格）无效，按原方向继续走." If bot returns opposite current, actual = original current direction. So achievable actual next directions: current_dir (via straight or invalid reverse), left, right. Cannot choose actual other than these except current. At spawn no current: all four.
Thus evaluate actual directions: if current_dir not None: [current_dir, left, right] (turn), not opposite. But what about if body first distinct not adjacent? same. If current none: all four.
We return corresponding chosen: for actual current, can return current_dir name (straight). So just ensure candidates = non-reverse unique directions.
- target in bounds.
- Build deadly_body set for current? For each snake, take body excluding last element? Actually post-move old body excluding unique tail = body[:-1] always (if len>1). If len==1, after move? length always >=3, but could body list length? Use body[:-1]. This includes all except current last segment. If last two duplicate, body[:-1] includes one duplicate at tail? Example [H,A,T,T], body[:-1]=[H,A,T]. Tail cell T remains, correct. If unique [H,A,T], body[:-1]=[H,A], T vacates. So simple: all segments except last element (one segment removed). Great.
For any snake including me, deadly_body |= set(body[:-1]). Wait for other snake's current tail unique, body[:-1] excludes last, safe. For duplicate, body[:-1] includes one T, so target T deadly. Good.
But does body[:-1] include current head; yes. So target current head deadly. Good.
For our own movement, target in own body[:-1] deadly. Our current tail unique excluded safe. Good.
Thus immediate body death if target in union(body[:-1] for all snakes alive). Note if target is current tail of a snake with duplicate, last two same; body[:-1] includes one duplicate at same coordinate, so deadly. Great.
- However if target is current head of a snake that will die before our collision due to wall etc? We still treat deadly. Fine.
- If target occupied by food and deadly? no.

So legal_body = not in body_after_occ where occ = set all body[:-1] for all snakes. Wait what about our current head cell in occ, but we move out. If target is another segment not our current head. For other snakes, their old head becomes neck and remains; so include. Yes.
What about target equals our current head? Cannot (dir zero); if reverse invalid actual current from head to next in front, not own head. fine.
Important: If another snake has length 1, body[:-1] empty, old head would move and not remain? But length min 3. Ignore.
- Health starvation if my health <=1 and target not in food -> death likely. Treat legal false unless no alternatives.

- Head-on danger:
  For each opponent, determine possible next head cells given its current direction; use body to infer. They cannot reverse; candidates [current, left,right]. But if current None all four. For safety, do we include all four? Using inferred. For each possible cell op_target (in bounds maybe they might die by body, but if they choose, they may). If op_target == my target:
      op_len_after = op["length"] + (1 if target in food_set else 0)
      my_len_after = my_len + (1 if target in food_set else 0)
      if op_len_after >= my_len_after: danger_heads += big; maybe classify fatal_contest.
      else: danger_heads += small (we can kill them if they come; but if multiple? They die, we survive. If two longer? all shorter? unique max us, survive. Good. If another equal/longer also, fatal already.)
  Also risk if target adjacent? We can penalize potential opponent cells one step away? But immediate enough.

Should we treat opponent possible current direction only? Other AIs may choose left/right. Yes possible. But they may also invalid reverse continue; included current.

Potential issue: If target in other snake possible next head and op longer, but that snake would die by colliding with body/wall if it chooses that, so it won't. Our penalty may overavoid. Could compute op move safety? We can filter opponent possible moves that don't hit body/wall? But they are other programs, they will avoid death. So only consider possible moves that are body-safe for them. However their safety depends on all bodies after movement including ours? If they move into our newhead, head-head. For risk, opponent wants not die; if shorter they avoid contest. But if longer, they might. We can approximate: possible op target if in bounds and not in body_after_occ? Body_after_occ includes all body[:-1], including our old body; but if op target equals our newhead not current body, not in occ. If op target in occ, they die by body and won't choose (unless no). So filter.
But op target equal our target: both newheads, not in occ (unless target current tail? etc). If opponent length >= ours, they could choose and kill us; they might if beneficial but risk if we choose elsewhere. Hard.
For danger scoring, for each opponent possible move that is body-legal for them (using current bodies post movement), if target equal my target and op_len_after >= my_len_after -> very high. If op_cell adjacent etc no.
Alternatively compute "danger cells" = possible safe next heads of opponents with longer/equal; penalize our candidate if in that set. Also maybe if our target is adjacent to such cell? Not immediate.

- Compute own next body if eat. new_body = [target] + my_body[:-1]; if target in food_set: new_body.append(new_body[-1])? Wait body after eat append copy of current tail after shrink = old_body[-2]? But if new_body currently [target]+old_body[:-1], last = old_body[-2] if len>1. Appending new_body[-1] duplicates last. That matches example? old [H,A,T], new_body [H',H,A], append A -> [H',H,A,A]. Yes append new_body[-1]. If old length? okay. But if old body last was duplicate [H,A,T,T], no eat: new_body [H',H,A,T] (length same; one duplicate removed). If eat: append T -> [H',H,A,T,T]. Correct. So use if target in food_set: new_body.append(new_body[-1]).
Length after = len(new_body) vs my length +1. state length might match. Use len(new_body) for own new length.
Health after = 100 if food else max(0, health-1).

- Space/flood:
  Build blocked set for open area. Need account all snakes after one movement? For our future, we know other snakes will move but not directions. To be conservative, perhaps use current body occupancy after tail removal = body[:-1] for all snakes? But our new head will be in a cell; our future body includes new_body excluding head. For accessible open from new head, blocked by all other current body after movement? Other bodies after movement include their current head plus body[:-1]; same as occ plus maybe? Actually body[:-1] already includes current head. Their current tails unique removed. So occ is exactly occupied cells after move excluding newheads (for all snakes) where those newheads unknown. It includes our old body except our current tail. But after our move, our old body shifted: new body cells include [head]+my_body[:-1]. Our new head may not be in occ. For flood from new head, block by:
       other snakes bodies after move: for each other, body[:-1] plus their unknown new head. Unknown new head can be ignored? It will be an occupied cell next turn, but moves. For future area, include current body[:-1] static; ignore other newheads.
       own new body excluding head? If we include all own body, flood cannot traverse through body, but the snake follows and may open tail. For static flood, include own new_body[1:] perhaps. This underestimates room if body blocks narrow corridors but more realistic for next immediate.
  For reachable area, we want cells the head could eventually roam without crossing walls and other bodies; own body should be avoided now, but moves. For trapped check, include own new_body[1:] as blocked (including tail) because cannot move through it. However tail will move, but within horizon can follow. Including tail conservative.
  Use blocked = union(body[:-1] for all snakes) but not including candidate target? Wait occ includes our old head etc. Our newbody will occupy old head and my_body[:-1]. For flood from candidate, we should include own new_body[1:] = my_body[:-1] (plus duplicate if ate); and other bodies = their body[:-1]. Since occ already includes my_body[:-1] and others. Good. But occ also includes our old tail if duplicate? my_body[:-1] excludes last; if eat appends duplicate at tail, new_body[1:] includes old_body[:-1]+append. Occ has old_body[:-1]; plus for eat, tail duplicate at coordinate old_body[-2], which is already in old_body[:-1]? Wait old_body[:-1] includes old_body[-2] as last. Appended duplicate same cell, no new coord. So blocked unchanged. For no eat, own new body [target]+old_body[:-1]. Thus blocked cells = occ (all body[:-1]) plus maybe other newheads unknown. So we can flood from candidate treating occ (including candidate? candidate not in occ because legal body not in occ) as blocked. Occ includes all old body except tails. It includes our old body cells; good.
  But note occ includes current heads of all snakes, including their old head which after their move becomes body. We include. It does not include our candidate. Good. It excludes other current unique tails; they may be free after their move. Good.
  For flood, allow cells not in occ and within bounds. Compute reachable from candidate excluding blocked. This gives area/mobility.

  Need maybe remove our candidate from blocked if it accidentally in occ? legal ensures not. For fallback maybe.

  Optimize flood: BFS using 2D coordinates, visited bitset or bool list. width,height small. For each candidate 4 times, BFS.
  Return area, and perhaps number of exits from candidate (neighbors free). If area < len(new_body)+2, trapped danger.

- Food distance:
  We can compute BFS from candidate through free cells (blocked=occ) to nearest food, also maybe weighted by health. But if food inside body? Food always empty not on snakes. Food can be in reachable. Do multi-source? For each candidate BFS distance to food. Could integrate in flood BFS and record min_food_dist. BFS through free+food. If candidate on food dist 0. Use BFS queue. At most 961.
  Also distance to each opponent? For aggression maybe.

- Additional metric: openness in 8-neighborhood; avoid corners.

- Future survival search: We can do a greedy depth-limited search for our snake from new_body on static occ to evaluate if can survive and eat. Could calculate max reachable area enough. Maybe implement a small beam search without per-candidate? Since each candidate has new_body. But 50ms, 4 candidates, depth 4 each = manageable. We can simulate our future moves avoiding static occ and own body, allowing tail movement. This gives dynamic space and food. Use static other bodies occ (including tails excluded) as obstacles fixed. Our own body moves, tail vacates. Search for best path to food, maximize area. But opponents move; static approximation maybe useful.

Implement recursive/beam:
 Function simulate_score(body, health, food_set, depth):
   Use BFS/DFS best over our possible moves for depth D (e.g., 4).
   State includes body tuple, health, foods eaten? Food set maybe remove eaten? For local search, if eat, food at target removed in this hypothetical; but actual other food remains. For path evaluation, can treat target food consumed and add reward but no need for future within 4? Could remove to avoid repeated. We can maintain used food bitset? Simpler greedy evaluate candidate depth 3 with food.
   Branch up to 3. At each move:
      direction not reverse current (from body first two; if duplicates all)
      target within, not in fixed_occ, not in body[:-1] (self collision after move)
      health after, if target food set health=100 else health-1; if health<=0 and not food? Actually if reach 0 before eat? If health becomes 0 and target not food, dead; if target food restored. In code health_after = 100 if target in foods else health-1. If <0? If health_after<=0 and target not food => die after step? If target food, 100. If health 0 after hunger then food restores, so only if no food and health<=1.
      new_body = [target]+body[:-1]; if target food: append duplicate; update food set remove target.
      Score incremental: reward food (e.g., +20), length, plus terminal flood area, penalty danger? Search max.
   Depth 3 maybe 3^3=27 per candidate, each step set operations, okay. Depth 5=243*4=972 states, okay. But flood at leaves maybe heavy. Could use depth 4 and use heuristic at leaf with area. 50ms; 4* up to 3^4=324 leaves, flood each 961 = 311k *? Actually 324*4? For each initial candidate 81 leaves depth4, flood each = 78k, times 4=311k per turn; 800=250M maybe okay but Python 50ms per turn. 311k cell visits per turn, ~0.02s? Could be okay. But if depth5 more. Need safe.
  We can do beam search instead: At each depth keep top K states by heuristic; evaluate final. Simpler evaluate candidate with 1-step flood and food distance; choose. Maybe enough competitive? Need stronger.

Maybe implement full Monte Carlo tree? No.

Let's consider expected opponents: other AI will use sophisticated search. Need our bot strong. But due prompt constraints, all top AI may write similar. Need include good survival.

Let's design an efficient "beam search" over our snake for horizon ~8 with beam width maybe 8, static obstacles current occupied body[:-1] (including other body), allowing tails of our own to move. Score states by:
- alive
- area reachable
- distance to nearest food
- health
- length
- head risk? Other bodies static, but heads move; incorporate danger map at initial? At each future step, other bodies static, head danger not simulated. We can penalize cells within possible opponent head in first step only.
 This search can find path to food and avoid dead ends. Since obstacles static, it may overfit but okay. For each initial candidate, run beam search 5-8 steps and evaluate best path. But 4 candidates * beam width * depth * BFS maybe.
Simpler: For each candidate, use greedy lookahead:
  - Score immediate metrics.
  - Also run 3-step survival search to check if at least can move next turns under static occ. If no future, penalize.
Since board small and 50ms, we can do a recursive max-search with alpha for each candidate depth 3. At leaves compute flood area. This will identify traps.

Let's estimate time: 4 candidates * branching <=3^depth. Depth 4 -> 324 leaves. If flood at each leaf (961), 311k cell checks; plus recursion overhead. 50 ms maybe 0.05s; 311k in Python ~0.01-0.03. Good. Depth 5 -> 972 leaves ~1M ~0.05 borderline. Use depth 4 or adaptive. For 31x31, 961 cells. Could cache flood area by (body,target)? Hard. Use depth 3 + immediate area. Or use local area not full BFS? Need safe.

We can optimize flood using 1D visited array of size N, queue list of ints. For each call allocate [False]*N (size 961), overhead okay. BFS neighbors with x/y or index. Use index r=y*W+x. We need blocked occupancy set. In search, static_blocked is fixed set of coordinates (other snakes bodies after tail removal plus maybe my initial tail? For our own body simulation handles). For flood area from a body head, blocked = static_blocked ∪ set(body[:-1]) for our dynamic body? In search dynamic body. For leaf, compute area considering dynamic body? We can compute open area from head treating static other bodies + own body excluding tail (or all except tail) as blocked. This may be expensive. But if we've searched survival, maybe leaf area using static_blocked only (excluding own body) to represent room, as own follows. Add mobility count (valid next moves) to score.

Search state body list current (after moves), health, foods set maybe local removed. We don't need exact food removal for 4 steps? Use original food_set; if pass over same food multiple within search due not removing, might overvalue returning. Better maintain foods bitmask or list. Board up to 961, Python int bitmask efficient. Compute food_mask for initial food cells (global positions). State food_mask; eating clears bit. For search depth small.

But doing food_mask updates with bit operations easy. Yet food set used for target. Use bit index = y*W+x. If target in food_mask: new_food = food_mask & ~(1<<idx). Health=100, grow. Need branch.

At leaves, evaluate:
  score = length*? + area reachable (static_blocked only maybe dynamic own?) + food potential.
Maybe just use recursive search to maximize cumulative reward:
  reward at each step: +1 per survival, +100 if eat (for 4 steps maybe), + (valid_moves -1)*2, + maybe -danger if initial.
  At depth end, add min(area, 20)*weight using BFS from head with blocked static_blocked ∪ body[1:]? But body moves. Could use static_blocked only to approximate room not occupied by others; own body ignored.
Search needs avoid body collisions with own body[:-1] and static_blocked. Note static_blocked includes our old body? We should not include our body in static_blocked, because dynamic own body handled. For other snakes, use their body[:-1]. Also include our current body? Dynamic includes our old body and moves. For initial after candidate, body new_body includes own old body. For future, collision check target not in body[:-1] (after move? Wait to choose next step from current body state, collision target in current body[:-1] after movement? At state body before movement, post-move own body = [target]+body[:-1]. Target cannot be in body[:-1]. Yes). Static_blocked from other snakes = union(their body[:-1]) excluding our snake. But their current head cells included; they will move too, but we keep static. Good. However initial legal already considered all snakes bodies; for future, other bodies static includes their old body except tails, may block cells. Since they move, conservative.
What about other snake tails? Excluded if unique. Good.
For initial candidate, if target in static_blocked_other or body[:-1], illegal. We can use new_body and static_blocked_other. But our dynamic body includes old body except tail; target was not in all body[:-1] including ours. If target eats, new_body append duplicate; no new head.

Need model other snake current heads in static_blocked: yes other body[:-1] includes current head, which after their move remains as neck. But in future steps >1, their old head may move? Actually their body follows, but static approximation treats all body[:-1] fixed forever. That may overly block. But for search horizon small, okay. Alternatively for future, other bodies move too, but unknown. We can reduce static_blocked to only other bodies excluding heads? Hmm for next step, current other head remains as neck; for step after, could move? Their body segments move forward; a cell current head may remain for many turns as body. Static fixed overestimates long-term blockage but safe. For room evaluation, maybe ignore static_blocked future? Let's keep.

Beam/recursive:
Because branch small, implement recursive DFS with depth limit D and evaluate leaf plus prune. We need choose best initial candidate. For each candidate, call search(new_body, health_after, food_mask, depth=D, current_dir=dir) returning best additional score. Search may return score including reward and leaf area.
But doing full DFS per initial candidate with food_mask and depth 4: 4*3^4=324 leaves. At each node moving.
Implement iterative beam search maybe faster and can handle score.
For each initial candidate, we can start a beam list of states (body tuple of coordinates, health, food_mask, dir, score_accum). For step in 1..D:
  For each state, generate next moves (max3) that are legal body/static, health.
  new_score = score_acc + step_reward: +5 survival, +50 if eat, +2*(mobility) maybe.
  Keep top beam width e.g., 6 states by new_score + heuristic (distance food, health/area approximate). This reduces computation. But top by immediate might miss. For 4 candidates, D=6, width 8: 4*6*8*3=576 expansions, each simple. At end evaluate each state with flood area. Very fast. Beam search could be strong.
Use beam search per initial candidate? Maybe instead combine all initial candidates into one beam with first move? Need choose first. We can evaluate each candidate separately.

State representation: body as tuple of (x,y), health, food_mask, dir, acc_score. Depth up to maybe 6. Body length can grow, up to many; copying list. Board 31, body length <=961 but usually <50. Fine.
At each state, determine current dir from body[0] and first distinct body[1]. Because in search we can track dir. For new state, dir = move vector.
Generate legal actual directions: current dir none all; else [cur, turn_left, turn_right]. Do not include reverse. But note invalid reverse could be returned as current; no need.
For each move:
 target = head+dir
 if out continue
 if target in static_blocked_other: continue (for other snake bodies fixed). Also target in body[:-1] self death. Wait current body includes head and segments. To simulate move, after tail removal own body = [target]+body[:-1]. If target in body[:-1], death. This excludes current tail unique (body[-1]); if body[-1]==body[-2], body[:-1] includes duplicate tail? Example body [H,A,T,T], body[:-1]=[H,A,T], target T equals one -> deadly, correct. If unique [H,A,T], target T not in body[:-1], safe; but if target has food and eats, tail removed then new tail duplicate of old A, T vacated; safe. Great.
 health: if target food bit: new_health=100; grow=True. else new_health=health-1. If new_health<=0? If no food and health<=1 then death in elimination. But search state current health after previous step. For move, if new_health<=0 and no food, invalid. If food, health=100. If new_health=0 but food? set100.
 new_body = [target]+list(body[:-1]); if grow: new_body.append(new_body[-1]).
 food_mask update.
 Accum score: + survival 1; + if food e.g. 40; + maybe + len(new_body)*0.01 no.
 Need heuristic for beam ranking at each depth. To choose top states before depth limit, use:
   h = accum + food_count*30 + new_len*5 + health*0.1 + rough_open
But rough_open BFS each expansion expensive. Could compute number of free neighbors around head not in static_blocked_other ∪ body[1:] as mobility within 1 or 2. For beam ranking use simple.
At final after D steps, for each state compute area reachable from head using blocked = static_blocked_other ∪ set(new_body[1:]) (own body as obstacles) or ignoring own? Let's include own body to see actual accessible immediate. BFS; area. Score = accum + area*2 + len*5 + health*0.1. Also danger from other possible heads maybe only initial? We already can include initial candidate head danger separately.
But static_blocked_other includes other current body[:-1], not their future moving; area might be small if near. Could use for trap.

Potential issue: Search may choose path that eats food and grows, but if food is contested by head risk not modeled. We add initial danger for target. Future danger not considered. Could include at each step? We can compute danger_cells for opponents' possible safe next heads from initial state; these are only valid for turn1. For future, positions change, can't. Use static danger around opponent heads? Maybe treat cells adjacent to opponent heads as risk if not longer. In search, penalize target if in current actual danger cells (initial) only at depth0. For future, other snakes will move; but static blocked includes heads; target adjacent may be safe due body. Hard. In multi, head-on important; initial candidate danger penalty enough.

Alternative evaluate candidates directly with 2-ply minimax of head collisions? We can compute for each candidate if target is possible head cell of longer opponent and opponent move is safe for them. Add huge penalty. Also if target is food and opponent likely goes there maybe avoid.

Let's define candidate scoring:
- If invalid body/out/health: score=-inf.
- head_risk:
  my_len_after = len(new_body)
  For each opp possible safe move cell == target:
      opp_len_after = opp_len + (1 if target in food_mask else 0)
      If opp_len_after >= my_len_after: risk += 10000 (fatal if they contest)
      Else: bonus_aggr += 20 (we may kill them) but risk if multiple? 
  Also if target is within one Manhattan of longer opp head and not blocked, small risk: count * -20.
But be careful: target might equal current head cell of opponent? That's in body_blocked, invalid already. Possible moves from opponent exclude body collision? Their possible target could be body_blocked for me? If target in my body? invalid. We should compute safe.
Opponent possible moves:
  op_current_dir infer from op body first distinct (head - seg sign).
  moves = [op_current, left, right] or all4.
  For each op_move target cell ot:
     Check if ot in bounds and ot not in body_after_occ? Wait for opp, body collision uses all body[:-1] (including ours). But if ot == my target, our old body maybe? Our target not in body_after_occ; fine. If ot in body_after_occ, opp would die by body (except head-head not in set). They likely won't. Filter out.
     However if ot equals my target and I will move there, from their perspective my old body not there, but my newhead is. They may deliberately contest. Safe by body.
     Their possible safe moves = ot in bounds and ot not in occ_all (body[:-1] all). But occ_all includes their own body[:-1], so excludes cells they would hit own body. It also includes my current body[:-1]; if they move into my old head/body, deadly, so filter. Good.
     What about if ot equals a current unique tail excluded from occ_all, safe. good.
  But if ot is my target, and my target may be in occ_all? We require legal target not in occ_all, so safe. Good.
Use moves filtered by body_safe for opponent. However if ot equals current tail of some snake unique, free; included.
For each safe op move == target, evaluate contest. If opp_len_after >= my_len_after => fatal risk. But opponent may not choose if they infer we are longer? If they are longer, they might choose. If equal, they avoid if possible, but could be forced. Penalize high but not impossible. If multiple directions, they may choose other. Fatal risk if they are already adjacent and target likely. Use high.
Also opponent's newhead could be our target but they may die if another longer? not.

- area: flood from target with blocked = occ_all? occ_all = union(body[:-1]) all snakes (after our move old bodies). But candidate not in occ. Need include other current heads etc. For area, use blocked = occ_all ∪ set(new_body[1:])? occ_all already includes our old body[:-1] = new_body[1:] except when eat duplicate no new coordinate. Includes all snakes body[:-1]. Use occ_all. BFS within board through cells not in occ_all. However occ_all includes current tail duplicate if not vacated. It also includes other snakes current unique tails? no. Good. It includes our old tail if duplicate; new_body[1:] same. It includes other snakes bodies that will move, conservative.
  But if candidate itself in occ? no.
  area = count reachable cells from target excluding blocked. Include target. If area < len(new_body)+1, likely trapped.
- distance to nearest food in this free region. Use BFS multi? For each candidate, we can compute min dist to any food via BFS; integrate into area BFS. Food cells are not blocked. Start target. Track min_food_dist. If health low, weight strongly. If no food reachable, dist large.
- mobility: number of free neighbors from new head excluding occupied and walls. Could use BFS first-level. BFS returns maybe.
- length bonus: new_len * e.g., 30 (survival priority and contest).
- health: if health low, prioritize food. Health after.
- turn/num context: early length important; late survival/control.
- danger area near opponents: maybe compute safe region size after removing cells adjacent to longer heads? We can approximate opponent territory. For candidate, count number of reachable cells that are within Manhattan? Too heavy. Could compute nearest opponent dist and penalize if in front of longer snake. In multi, avoid being in front of longer head. For each opp with length>=my_len, if target is along possible path? Compute Manhattan distance from target to opp head; if <=2 and in line, penalty. Simpler head_risk covers possible next. For future, being adjacent to opponent can be dangerous. Add penalty for distance 1/2 to longer opponent head, except if target food and we're much longer? Maybe.
- Aggression: If my length > opp and distance small, target in their possible next head => bonus. But our head risk logic. For survival, avoiding longer more important.

- Search score (future) could incorporate area and food; choose candidate by final combined.

Let's design code structure clean.

Global variables? Could use random? Standard.

Directions:
DIRS = [(0,-1,'up'), (0,1,'down'), (-1,0,'left'), (1,0,'right')]
opposite mapping by vector.
Direction name from vector.

Helper infer_dir(body):
 if len<2 return None
 hx,hy=body[0]
 for seg in body[1:]:
   dx=hx-seg[0]; dy=hy-seg[1]
   if dx or dy:
      # normalize sign to unit; if abs >1 due multiple duplicate? sign
      if dx>0: return (1,0)
      if dx<0: return (-1,0)
      if dy>0: return (0,1)
      if dy<0: return (0,-1)
 return None
Because body coordinate values ints.

actual_moves(cur):
 if cur is None: all 4 vectors
 else:
   left = (cur[1], -cur[0])? Need coordinate y down. For vector (dx,dy), left/right relative to snake. A snake moving dir, it cannot reverse. It can go straight, turn perpendicular. Both perpendicular are valid regardless left/right. The two perpendicular vectors: (-dy, dx) and (dy, -dx). Include cur. So set [cur, (-dy,dx), (dy,-dx)].
No need distinguish name.
Mapping to name: dict.

Immediate body_block:
For each snake, body = s["body"]; for seg in body[:-1]: add tuple. Note if length maybe body length >1. If body only one, body[:-1] empty, but after move old head? Length min3. okay.
Do we exclude dead? snakes only alive.
Need include our snake; candidate legal not in occ_all. For target equals our own current tail unique (body[-1]) and tail unique, body[:-1] excludes last. If another snake also occupies that tail? occ_all maybe has from other body, then target in occ due other, death (head hits other body). If target simultaneously current tail of self and other body, invalid. Good.
But what about target equals current tail of self that is also food? impossible food not on snake.
Head-on target could be in occ_all if it is current tail of another unique? It is excluded, safe. If another snake possible move there, head-head. fine.

Flood BFS details:
def flood_area(start, blocked, W,H, food_set=None):
  O(W*H) visited using bytearray? Bytearray is fast. But allocate [0]*N each call.
  Use index = y*W+x. Blocked set of coordinates; need check target in blocked in neighbor. Converting blocked to set of indices improves speed. For each candidate, occ_idx set? Body_block coordinates set. For BFS, check idx in blocked_idx. blocked_idx fixed per turn (occ_all). For search dynamic body, need separate.
  For candidate area, blocked_idx = set(y*W+x for seg in occ_all). start index not blocked. BFS queue list preallocated? Simple deque from collections, but standard. Use list with head index for speed:
    seen = bytearray(N)
    if blocked_idx[start]: return 0? candidate legal not.
    q=[start]; seen[start]=1; qi=0; area=0; min_dist=999; dist array? To compute food distance, need dist. Could use visited with distances? Use separate dist list? Or BFS layer.
    Since need area and nearest food, we can perform BFS and track distance when encountering food. Use queue of idx and parallel dist or use dist array. N <=961, allocate dist list [-1]*N each call maybe okay. Or BFS layer: current queue; for d loop. Need area count and if any food in layer, min_dist=d. Food indices set. Use q for nodes, dist can be encoded? Use queue list with tuples? Better maintain dist array initialized -1. But per call 961*alloc, okay.
  For each pop idx, check food: if idx in food_idx and dist<min...
  Explore neighbors. Need efficient neighbor calculation:
    x = idx % W; y = idx // W. Mod/div per node expensive but okay. Can precompute neighbor indices list for each idx for given W,H? Within a game W fixed, but module globals per game reset. Could build once in decide? State width same. We can cache neighbors global. But simpler compute:
      if idx >= W: n=idx-W up
      if idx < N-W: n=idx+W down
      if idx % W !=0: n=idx-1 left
      if idx % W != W-1: n=idx+1 right
    Mod per pop. Fine.
  Need blocked_idx contains indices. Check seen[n] or n in blocked_idx. Use bytearray blocked_bool for faster. Build blocked_bool = bytearray(N); for seg set 1. For flood, check if blocked_bool[n]. For dynamic body maybe build each call? For candidate fixed blocked_bool of occ_all (not including candidate; if candidate is in blocked_bool? legal no). For search final, blocked includes dynamic body; can build bytearray from static and body.
  For nearest food, food_bool? Could check if n in food_set coordinates; use bit mask? BFS for area can also compute min food by maintaining food_bool bytearray N.
  Given N small, in candidate flood function:
    def bfs_metrics(start_idx, blocked_bool, food_bool, N,W,H):
       seen=bytearray(N); q=[0]*N; use list append maybe.
       q=[start]; seen[start]=1; dist=[-1]*? Instead store parallel dist list qd? Use dist list of int N with -1, but allocate.
       We can process levels:
          q=[start]; seen[start]=1; area=0; d=0; min_food=99
          while q:
             nextq=[]
             for idx in q: area +=1; if food_bool[idx] and d<min: min_food=d; for n...
             q=nextq; d+=1
          This allocates many lists but N small.
       Return area,min_food, mobility maybe. Mobility can count free neighbors of start from blocked_bool.
  Simpler use deque? import collections. Standard allowed. Level BFS with deque and dist. Let's write efficient.
  Need avoid wall. Use helper neighbors maybe.

For search per move, we don't necessarily need flood every node. Beam search final only.

Let's decide final algorithm:

At decide:
1. Parse state, find me.
2. If turn maybe first spawn. If len(my_body)==1? not.
3. Build occ_all = set of all body segments except last for each snake (coordinates).
   Also occ_bool for all.
   Build food_set coords, food_mask bit for initial foods.
   Build other_blocked = occ_all minus my body[:-1]? For search static_other = set of other snake body[:-1]. Exclude all my segments. Since occ_all includes my old body, but search dynamic own body handles current; static_other should be other snakes' post-move body excluding tails. Build other_blocked set and bool. Need for search legal: target not in other_blocked and not in body[:-1]. Note initial candidate legal target not in occ_all = other_blocked ∪ my_body[:-1], same.
4. Infer my current dir. Determine actual moves [cur, perp, perp] unique. For spawn cur None all4. For each move vector:
    target = head+vec
    Check bounds, not in occ_all, not starvation if health<=1 and target no food (and no? if health 0? health state could be1, after hunger0; if no food eliminated. If target food survive).
    Simulate new_body: list [target] + my_body[:-1]; grow = target in food_set; if grow append new_body[-1].
    health_after = 100 if grow else my_health-1. If health_after<=0 and not grow? invalid. Actually if my_health-1 <=0; if grow health=100. So invalid if health_after<=0. But if health=1 and no grow, invalid. If health=0 impossible alive? Could be alive? health decreases at end, if 0 eliminated. no.
    Compute head_risk. Need possible opponent safe moves.
      We can precompute per opponent possible safe head cells? For each opponent snake (alive, id != you):
         op body. op_cur = infer_dir.
         op_moves actual [cur, perps] or all4.
         For each op_vec:
            ot = op_head + vec
            if out continue
            if ot in occ_all: continue  # body collision for opponent using all bodies[:-1], but note if ot == my target? my target not in occ_all, so not skipped. If ot is current unique tail excluded, safe.
            # What about ot == op own current head? no move zero.
            # What about ot equals another newhead? head-head unknown; safe body.
            op_len_after = op_len + (1 if ot in food_set else 0)
            record (ot, op_len_after)
       Could be duplicate from one snake? moves unique usually. For each candidate target, check records where ot==target.
       If op_len_after >= my_len_after: fatal_risk += 1 (or weight)
       elif op_len_after < my_len_after: aggr += 1.
       Also proximity risk: for each opponent head distance Manhattan <=? We'll compute separately.
      Note if op move ot in occ_all due current body, filtered; but what if ot is our target and target has food? occ_all doesn't contain food, okay.
      Build op_head list for proximity.
    Score initial:
       base = 0
       if fatal_risk: score -= 5000 * fatal_risk
       else maybe safe.
       if aggr: score += 50*aggr (but contested only if they choose; small)
       # length/health
       score += len(new_body)*20
       if grow: score += 150
       score += health_after*0.5
       # Area/food BFS with blocked=occ_all (post movement excluding newheads). But candidate target is not in occ_all. Use blocked_bool_occ_all.
       area, food_dist = bfs_metrics(target_idx, blocked_bool_all, food_bool)
       # But blocked_bool_all includes current tails excluded unique. It includes our old body etc. Does it include candidate? no.
       # Add area reward with cap. More open better. If area < len(new_body)+2, penalty huge.
       req = len(new_body)+2
       if area < req: score -= (req-area)*200
       score += min(area, 80)*3   # large area
       # food urgency
       health=health_after
       if food_dist<99:
          if health < 40: score += max(0, 200 - food_dist*20)
          else: score += max(0, 80 - food_dist*8)
       else:
          if health < 60: score -= 200
       # mobility from target maybe number free neighbors (from BFS could compute)
       # Proximity to longer opponents
       for op in snakes:
          if op.id==you continue
          d = manhattan(target, op_head)
          if op_len >= len(new_body):
             if d==1: score -= 120
             elif d==2: score -= 30
             elif d==3: score -=5
          else:
             # can chase shorter if very close and no risk
             if d==1: score += 10
       # centrality maybe
       # Search future using beam
       search_score = beam_search(new_body, health_after, food_mask_after, cur_vec=vec, other_blocked_bool/set, W,H, food_set? Use mask, depth based)
       total = score + search_score
    Store candidate (total, vec, details).
5. Choose highest total. If no legal, fallback:
   consider moves in order, avoid out, choose one maximizing free neighbors/area ignoring death; return name. Could use original direction if valid.
6. Return direction name for chosen vec.

Beam search design:
We need it fast and effective. Could run per candidate. But initial score already includes area. Search can improve path to food avoiding dead ends.
Function beam_search(initial_body, health, food_mask, init_dir, other_blocked_set, W,H, depth):
  states = list of tuples (body_tuple/list, health, food_mask, dir, accum)
  for step in range(depth):
    new_states=[]
    for each state:
      generate moves as above, legal against other_blocked and self body.
      For each:
        grow etc.
        accum2 = accum + 1 (survival) + (40 if grow else 0) + maybe small for health restoration.
        # heuristic for pruning at this depth:
        h = accum2 + len(new_body)*2 + health*0.05
        # rough mobility: count open neighbors around newhead not in other_blocked and not in new_body[1:] (maybe up to4)
        mob = ...
        h += mob*2
        # distance to nearest food? Compute Manhattan to nearest food bit; but food_mask maybe. Use global food_coords? Could precompute list from mask? For speed, maintain food_list? But mask bit; during beam small. We can compute Manhattan to nearest food by iterating original food coords (<=3 or12) per generated state; cheap. If target/grow removed, need ignore eaten? For heuristic, use any food in food_mask. Iterate food_coords_initial and check bit. 12*states. Fine.
        d = min manhattan(head, food) among mask bits
        h -= d*2 (closer better)
        # If health low, weight d more.
        if health<30: h -= d*5
        new_states.append((h, body_tuple, health, food_mask, dir, accum2))
    Keep top beam_width by h. If no states, break.
  At final, for each state compute flood area with blocked = other_blocked_set plus set(body[1:])? For search final. Build blocked_bool dynamic maybe. Use bfs_area_no_food. Score = accum + area*3 + len(body)*10 + health*0.2.
  Return max score - baseline? Need comparable with initial score. If search_score includes length and area similarly, could double count. We can make beam returns additional future value only, e.g., best final score / scale. But choose candidate relative; okay.
  Baseline for no search maybe. For each candidate, search includes its initial state after first move. It returns best cumulative future reward (next steps). It should not include initial candidate length? Accum starts 0. At final add area*? and len*? This can favor larger length, already in initial. We can keep small.
  Simpler: search returns best value = accum + final_area*2 + final_len*2. Initial score includes immediate; candidates compared with same current length plus maybe grow. Double length not huge. Good.
  Depth: For duel (num_snakes==2), depth=7, beam_width=10. For multi, depth=5, beam_width=8. Time? Per candidate: depth*beam_width*branch ~ 7*10*3=210 expansions; final area for up to10 states per candidate =>40 BFS of 961=38k; 4 candidates=152k, fine. Actually beam search per candidate 4; 4*210=840 expansions simple. BFS final 4*10=40*961=38k. Very safe. Could increase depth 10, width 12. 50ms. Let's estimate Python 800 turns; need per turn <50ms. 800 expansions + BFS ~ okay. Use adaptive:
    if width*height <= 255 (15x15): depth=10, beam_width=12
    else: depth=7, beam_width=10
  Full BFS final per state maybe 12*4*961=46k, negligible.
  Each expansion computes mobility and nearest food by iterating food coords. Good.

But beam search sorted each step. Use list of states with h; use heapq.nlargest? Beam width small, can sort list length <= beam*3 <=36; sorting trivial.
State representation: To avoid duplicate states maybe not needed. Body length can be >? tuple of coords. Building set for self each expansion? We need check target in body[:-1]. Body tuple slicing creates; could use set(body[:-1]) per state precomputed? State can include body tuple; for each expansion, target in body_set? But new_body changes. For legal, check target in body[:-1]. Since body length small, using `target in body_tuple[:-1]` O(L) maybe L up to 100 and expansions ~800 ->80k, fine. But repeated per move. Could maintain body_set and tail? Tail vacates, so target not in body_set except tail might be allowed if unique. Need precise. Use `target in body_tuple[:-1]` fine.
Check other_blocked_set target.
Health starvation.
Food mask and coords.
Generate moves for current dir `cur` stored. But if cur is None all4. Use cur and perpendicular.
Directions order irrelevant.
For new dir, actual move vector.
When grow, new_body = (target,) + body[:-1] + (body[-2]? Wait using body tuple before movement. Earlier formula if grow append new_body[-1] = body[-2] if len>1. But if body[:-1] empty? Not. Using list:
  nb_list = [target] + list(body[:-1])
  if grow: nb_list.append(nb_list[-1])
  nb=tuple(nb_list)
This duplicates current tail after shrink (old_body[-2]) because nb_list[-1] = body[-2] if len(body)>=2. If body length 1, nb_list[-1]=target, append target; but min3. Good.
Food mask: idx target if bit set. For health, if grow new_health=100 else health-1. If new_health<=0 and not grow invalid (if health=1). In search, if no grow and health<=1 invalid. Note if health may be 0 only dead. Use if new_health <=0: continue.
Mobility: count neighbors from target that are in bounds, not in other_blocked, and not in nb_list[1:] (but tail unique maybe will vacate next turn; for rough open, use not in nb_list[1:] including tail; okay). If target count.
Nearest food distance among food_mask bits: Iterate `food_coords` global captured. But food_mask may have bits for initial foods; after eating removed. Need map idx to coord. Have food_coords list and food_bits list (idx, x,y). For each state, iterate global food_coords and if mask & (1<<idx). Up to 12, fine.
Manhattan from newhead to food.
Heuristic h = accum2 + length*1.5 + mobility*3 + health*0.1 - d*(3 if health>30 else 6). Also maybe penalize if mobility<=1. Add `if mob<=1: h-=20`.
At final: compute area using blocked other_blocked + body[1:]? Need BFS. We can compute open area with dynamic body:
  blocked_idx = other_blocked_idx? For search, other_blocked_set coordinates; plus body segments except head (all body? If include unique tail, for current state before next move tail will vacate; but area accessible from head now with tail considered occupied. Since snake can follow tail, include all body[1:] conservative. Use body[1:] as blocked. Build visited bytearray. BFS from head index; cannot pass through own body or other bodies. Return area. Score = accum + area*2.5 + len(body)*8 + health*0.2.
  Since accum includes rewards for growth, length bonus maybe too much; but okay.

Need convert coordinates to indices. We can use coordinate tuples in search; other_blocked_set coords. For BFS final, use W,H and blocked coords -> bool. Start target/head coordinate. Use idx = y*W+x. In BFS, check coordinate n? Could use coord set and BFS on (x,y) tuples to simplify but slower. N small. Use index and blocked_idx set built for state: other_blocked_idx fixed set plus indices of body[1:]. other_blocked_idx global for search? We can pass other_blocked_idx set. Build blocked_bool from static other blocked once per candidate? Static other_blocked same for all search. For each final state, create blocked_bool = bytearray(N); mark other_blocked_idx (pre-marked template copy) and body[1:]. Copying bytearray of size up to961 * states*candidates ~ 40*4=160, trivial.
Actually other_blocked template bytearray can be copied with `blocked = other_blocked_bool[:]`. Then mark body[1:] indices.
BFS area function:
def area_from_head(head, body, other_blocked_bool, N,W,H):
  blocked = other_blocked_bool[:]  # bytearray
  for seg in body[1:]: blocked[seg.y*W+seg.x]=1
  start=...
  if blocked[start]: maybe 0 (should not)
  visited=bytearray(N); q=[start]; visited[start]=1; count=0; qi=0
  while qi<len(q):
     idx=q[qi]; qi+=1; count+=1
     # neighbors if not blocked and not visited
  return count
Use list append.

Candidate flood metrics can reuse BFS generic. Instead of separate functions maybe implement.

Potential simplification: Implement helper get_neighbors(idx) inline.

Time constraints 50ms. Python code with beam search plus BFS per candidate/final should be under. But need be careful no excessive allocation in 800 turns. We can optimize enough.

Let's write functions in bot.py. Since loaded once per game, functions global.

Pseudo code:

from collections import deque? Can use list queue.

DIR_VECS = [(0,-1),(0,1),(-1,0),(1,0)]
DIR_NAMES = {(0,-1):"up",...}

def infer_dir(body):
    if not body or len(body)<2: return None
    hx,hy=body[0]
    for seg in body[1:]:
        dx=hx-seg[0]; dy=hy-seg[1]
        if dx or dy:
            if dx>0: return (1,0)
            if dx<0: return (-1,0)
            if dy>0: return (0,1)
            if dy<0: return (0,-1)
    return None

def legal_moves(cur):
    if cur is None: return DIR_VECS.copy()
    dx,dy=cur
    res=[(dx,dy)]
    p1=(-dy,dx)
    p2=(dy,-dx)
    if p1 not in res: res.append(p1)
    if p2 not in res: res.append(p2)
    return res

But perpendicular order maybe both. Directions are unit.

def manhattan(x1,y1,x2,y2): abs...

def bfs_metrics(start_idx, blocked_bool, food_mask, food_bits, W,H, N):
  # food_mask int; need check if idx food. Could precompute food_bool? For candidate food_mask initial. In BFS, when visiting idx, check if food_mask & (1<<idx)? Shifting per node expensive. Build food_bool? For candidate, initial food coords small; can track nearest by BFS all cells and if idx in food_idx set. Use food_bool bytearray N for current food_mask? For candidate initial, build food_bool_initial. For search final no food distance. So candidate BFS can use food_idx set.
  seen=bytearray(N)
  q=[start_idx]; seen[start_idx]=1; qi=0; area=0; min_food=999
  # We need distances; use parallel qd list? Use level BFS:
  dist=0; current_level=[start_idx]; seen...
  while current_level:
     next_level=[]
     for idx in current_level:
        area+=1
        if idx in food_idx and dist<min_food: min_food=dist
        x=idx%W; y=idx//W? For neighbors, derive.
        # up
        if y>0:
           n=idx-W; if not seen[n] and not blocked_bool[n]: seen[n]=1; next_level.append(n)
        ...
     current_level=next_level; dist+=1
  return area, min_food
Could avoid y calc by precompute bool:
  # Since W,H known, use idx >= W for up, idx < N-W down, idx%W !=0 left, idx%W !=W-1 right. Need modulo for left/right.
  up = idx-W if idx>=W else -1
  down = idx+W if idx<N-W else -1
  left = idx-1 if idx%W else -1
  right = idx+1 if idx%W != W-1 else -1
Use if n>=0.
Modulo per node. okay.
  Food idx set.

For mobility, can count free neighbors of start from blocked_bool and maybe self body included. In candidate blocked_bool_all includes occ_all (including our body). But candidate's new body duplicate tail etc. For immediate mobility, need avoid own new_body[1:] and other bodies. blocked_bool_all includes all body[:-1] including own old body, which after our move includes old body[:-1], same as new_body[1:] except if grow duplicate no new coordinate. So blocked_bool_all is suitable. Count neighbors of start not blocked/wall. Use function count_moves(start_idx, blocked_bool,...).

Candidate BFS blocked: Use occ_bool (all body[:-1]). Does this include current tail unique? no. Does it include target if target is current tail unique? no, free. Good. If our candidate is current tail of self unique, start not blocked. After moving there, our old body shifts; tail removed. The cell becomes newhead. blocked_bool doesn't include old tail, okay. It also doesn't include current head? It includes current head in occ. But after move, current head remains as neck, so blocked. Start different. Good.

Potential issue: occ_bool includes other snake current head but if that snake dies due wall this turn, its body disappears and block should removed. We ignore. Conservative.

Search static other_blocked_bool: union of body[:-1] for snakes id != you. It excludes my current body entirely. In beam search, initial new_body includes my old body[:-1], and target. For future, self collision handles own body. Other snakes static. Good.
But search doesn't include food as obstacle.

Danger calculation:
We need opp possible moves and safe. Let's implement within candidate loop perhaps precompute once per decide to reduce. For each opponent, possible next target cells and length after depending on whether cell has food. Since target cell variable uses food at target. We can precompute records list of (ot_x,ot_y,op_len,op_id). For each opponent:
  op_body; op_head; cur=infer_dir(op_body)
  moves = legal_moves(cur)
  for vec in moves:
     ox,oy = head+vec; if out continue
     if (ox,oy) in occ_all: continue  # body collision for op after movement using current bodies excluding tails. But wait occ_all includes op's own body[:-1]. If op moves straight, target could be current neck? no, current neck is body[1], not in front unless growing overlap. If target in own body[:-1] except maybe current tail unique excluded, unsafe. Good.
     # Also starvation? ignore.
     records.append((ox,oy, op_len, op_snake_id))
But if op target equals current unique tail of another snake, occ_all excludes, safe. If multiple opponent snakes possible same target, records multiple.
Then for each candidate target, iterate records. There are up to 10*3=30, fine.
  my_len_after = len(new_body)
  risk=0; aggr=0
  for rx,ry,olen,oid in records:
     if rx==tx and ry==ty:
        olen_after = olen + (1 if (tx,ty) in food_set else 0)
        if olen_after >= my_len_after: risk += 1
        else: aggr += 1
 Note if record from opponent would move into its own body? filtered by occ_all. But occ_all includes our current body; if target is our current unique tail, excluded. If opponent moves into our current unique tail while we move away? Could be safe; record included. If we also target there, head-head. okay.
For proximity, use opponent heads and lengths. We can use original snakes.

Could refine: For risk, only consider opponent moves that are truly safe after considering head-head with other snakes? Not.

If risk high, candidate score penalty. But what if target has food and opponent shorter, we survive and kill; bonus. If op longer, fatal if they choose. Since they may not choose, severe but not infinite. If all moves risky, need choose least. Use risk penalty 10000 so avoids unless forced. If equal and target is only safe, could still choose. Search score may override? Ensure risk huge.

Fallback if no candidate due body/starvation. Our candidate generation may skip all because occ all blocks. Need choose something. We can create candidates with bad flags. Approach: Build candidate list even if illegal body? If target out skip. If target in occ_all, mark invalid; but maybe all invalid. For fallback, choose actual move maximizing number of free neighbors ignoring collision? Better to return any non-reverse safe wall; if collides dies. We'll generate all actual moves with scores, invalid score -1e9 plus area ignoring bodies? Simpler:
  candidates initially include legal moves.
  If none, for vec in actual moves:
     target out? skip; choose one with max Manhattan to body? We can score = count in-bounds neighbors.
     Return first safe wall. But if no non-wall choose any.
Given spawn etc likely always legal.

Candidate Score calculation more concretely:

food_set as set of tuples for current state. food_mask build by bit idx for each food.
food_idx_set for BFS maybe set of idx.
occ_all coords set and occ_bool.
other_blocked_set, other_blocked_bool, other_blocked_idx.

For each candidate:
  tx,ty; target_idx.
  grow = (tx,ty) in food_set
  new_body = [target] + my_body[:-1]; if grow append new_body[-1].
  new_len = len(new_body)
  health_after=100 if grow else my_health-1
  if health_after<=0 and not grow? actually if grow health=100. If not grow and health_after<=0 invalid. If my_health maybe 0? skip.
  self body collision already via occ_all. But occ_all includes all body[:-1], target not in. Good.
  Risk:
    ...
  Score:
    score = 0.0
    score += new_len * 25.0
    if grow: score += 180.0
    score += min(health_after,100)*0.4
    # Avoid risk
    score -= risk * 4000.0
    score += aggr * 40.0 (but if risk also? If same target one longer and one shorter, contest: if longer present we might die; risk. shorter irrelevant.)
    # BFS metrics
    area, food_dist = bfs_metrics(target_idx, occ_bool, food_idx_set, W,H,N)
    # Note occ_bool includes current head etc. Does it include candidate's new duplicate tail if grow? no new coordinate, same as old. okay.
    score += min(area, 150) * 4.0
    # reward for mobility at target
    mob = count_free_neighbors(target_idx, occ_bool, W,H,N)
    score += mob * 8.0
    if area < new_len + 2: score -= (new_len + 2 - area) * 150.0
    if mob == 0 and area <=1: score -= 500
    # Food
    if food_dist<999:
       if health_after < 30:
          score += max(0, 300 - food_dist*30)
       elif health_after < 60:
          score += max(0, 140 - food_dist*10)
       else:
          score += max(0, 70 - food_dist*7)
    else:
       if health_after < 60: score -= 300
    # health urgency: if health<20, reward food even more and penalize no
    if health_after < 20:
       score -= 200
    # Proximity to longer opponents
    for s in snakes:
      if id==you: continue
      ox,oy=s["body"][0]; olen=s["length"] maybe len? use s.get length len(body). Use `s["length"]` but duplicates? length given. For contest use given length. new_len from body includes duplicates; state length matches len body likely. Use s["length"].
      d=abs(tx-ox)+abs(ty-oy)
      if s["length"] >= new_len:
          if d==1: score -=100
          elif d==2: score -=25
          elif d==3: score -=5
      else:
          if d==1: score +=15
    # Centrality: distance to wall min maybe
    edge = min(tx,ty,W-1-tx,H-1-ty)
    score += edge*1.5
    # Future search
    search_val = beam_search(new_body, health_after, food_mask_after, vec, other_blocked_set, other_blocked_bool, W,H,N, food_coords, depth, beam)
    score += search_val
  Choose.

Need adjust beam_search return scale comparable. Let's write beam_search:
def beam_search(body_list, health, food_mask, cur_vec, other_blocked_set, other_blocked_bool, W,H,N, food_coords, depth, beamw):
    # body tuple
    body=tuple((x,y) for x,y in body_list)
    states=[(body, health, food_mask, cur_vec, 0.0)]
    for step in range(depth):
       expanded=[]
       for (b,h,mask,cur,acc) in states:
          head=b[0]
          moves=legal_moves(cur)
          for vec in moves:
             tx=head[0]+vec[0]; ty=head[1]+vec[1]
             if tx<0 or tx>=W or ty<0 or ty>=H: continue
             if (tx,ty) in other_blocked_set: continue
             # self body collision: target in b[:-1]
             # Use loop to avoid creating set? b is tuple of tuples. `if (tx,ty) in b[:-1]` creates slice. Use for i in range(1,len(b)): if b[i]==(tx,ty): bad. But need exclude last? Wait body post-move removes last segment. Collision target in current body[:-1], i.e., indices 0..len-2? Python b[:-1] excludes last. It includes head and all except tail. We can check indices 1..len(b)-2? Current head index0 irrelevant target cannot equal head except zero direction; but include for safety. `target in b[:-1]` includes head. Use manual:
                bad=False
                for i in range(len(b)-1): # 0..len-2
                   if b[i]==(tx,ty): bad=True; break
                if bad: continue
             # health
             idx=ty*W+tx
             grow = (mask >> idx) & 1
             if grow:
                nh=100
             else:
                nh=h-1
                if nh<=0: continue
             # new body list
             nb_list=[(tx,ty)]
             nb_list.extend(b[:-1])
             if grow:
                nb_list.append(nb_list[-1])
             nb=tuple(nb_list)
             nmask = mask & ~(1<<idx) if grow else mask
             # mobility
             mob=0
             for dvec in DIR_VECS:
               nx=tx+dvec[0]; ny=ty+dvec[1]
               if 0<=nx<W and 0<=ny<H and (nx,ny) not in other_blocked_set:
                  # not in nb[1:]?
                  if (nx,ny) not in nb[1:]: mob+=1
             # nearest food
             mind=999
             for i,fc in enumerate(food_coords):
                if (nmask >> (fc[1]*W+fc[0])) & 1:
                    d=abs(tx-fc[0])+abs(ty-fc[1])
                    if d<mind: mind=d
             acc2=acc + 1.0 + (45.0 if grow else 0)
             # If grow heal, add health benefit
             if grow and h<60: acc2 += (100-h)*0.2
             # heuristic hval
             hval=acc2 + len(nb)*1.5 + mob*4.0 + nh*0.05 - (mind*2.5 if mind<999 else 0)
             if nh<40 and mind<999: hval -= mind*3.0
             if mob==0: hval-=50
             expanded.append((hval, nb, nh, nmask, vec, acc2))
       if not expanded: break
       expanded.sort(key=lambda z:z[0], reverse=True)
       # deduplicate? optional. We can take top beamw.
       states=[]
       seen_h=set()
       for item in expanded:
           hval, nb, nh, nmask, vec, acc2 = item
           # use a key of head/body maybe to avoid duplicates
           key=(nb, nh, nmask, vec)
           # body tuple hash okay; but unnecessary.
           states.append((nb, nh, nmask, vec, acc2))
           if len(states)>=beamw: break
    # evaluate states
    best=-1e9
    for b,h,mask,cur,acc in states:
       # area from head with other_blocked + self body[1:]
       # Build blocked bool from other_blocked_bool copy; mark body[1:]
       blocked=bytearray(other_blocked_bool)  # copy
       for seg in b[1:]:
          blocked[seg[1]*W+seg[0]]=1
       start= b[0][1]*W+b[0][0]
       if blocked[start]:
           area=0
       else:
           seen=bytearray(N)
           q=[start]; seen[start]=1; qi=0; area=0
           while qi<len(q):
             idx=q[qi]; qi+=1; area+=1
             # up
             if idx>=W:
                n=idx-W
                if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
             if idx<N-W:
                n=idx+W
                if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
             if idx%W!=0:
                n=idx-1
                if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
             if idx%W!=W-1:
                n=idx+1
                if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
       val = acc + area*2.5 + len(b)*6.0 + h*0.1
       if val>best: best=val
    return best
Need note other_blocked_bool passed includes other snakes body[:-1]. For search moves, check (tx,ty) in other_blocked_set. The body b includes our snake. Initial new_body may include our old body[:-1] and target. Good. If occupied by other snake unique tail excluded? Search treats other unique tails free (since other_blocked body[:-1] excludes), but in future other snake tail cell may be occupied by moving? static approximation. okay.

Potential issue in search: self collision check target in b[:-1] (current body excluding last). This allows target equal current tail if unique. If body last duplicate, b[:-1] includes last duplicate at same coordinate? For b with duplicate [H,A,T,T], b[:-1] = [H,A,T], target T is in, so disallow. Correct. If no duplicate [H,A,T], b[:-1]=[H,A], target T allowed; after moving, body [T,H,A], old tail T becomes newhead and vacated? Wait target T is old tail. Movement simultaneous: tail shrinks (removes T) while head moves into T. This is allowed in snake (following tail). Our simulation new_body = [target]+b[:-1] = [T,H,A]. That includes old tail as newhead, old A as tail (because removed old T). No duplicate unless grow. This is correct. Good.

When grow and target old tail? body b[:-1] excludes old tail; nb=[T,H,A], append A -> [T,H,A,A]. The old tail T is newhead with food? But can old tail have food? Current tail body cell cannot have food. So grow false if target tail. Good.

Search health: If h=1 and target food, grow True -> nh=100. If no food, h-1=0; code `if nh<=0: continue` before considering if no food. If grow, skip decrement and nh=100. Good.
Candidate health similar: if not grow and my_health<=1 invalid. If grow health=100.

Food mask building:
food_coords = [tuple(f) for f in state["food"]]
food_mask=0; food_set=set(); food_idx_set=set()
for x,y in food_coords:
  idx=y*W+x; food_mask |= 1<<idx; food_set.add((x,y)); food_idx_set.add(idx)

occ_all:
occ_set=set()
for s in snakes:
  b=s["body"]
  for seg in b[:-1]:
     occ_set.add((seg[0],seg[1]))
Need if b length maybe 0? no.
occ_bool=bytearray(N); for coords set occ_bool[y*W+x]=1.
Note if a cell appears in body[:-1] of one snake but is unique tail of another? occupied anyway.

other_blocked_set:
for s in snakes if s["id"]!=you:
  for seg in s["body"][:-1]: add.
other_blocked_bool similarly. Note excludes my snake entirely. It includes other snakes current body except unique tails; includes their heads. For search static.

Candidate legal: target not in occ_set. But wait occ_set includes our own current tail if duplicate? body[:-1] includes duplicate tail, correct. Excludes unique tail. It includes other unique tails? excludes. If target is in another snake's unique tail and also in another body? occ includes if other body. Good.
Should we also forbid target where another snake's current head will remain as body? occ includes all current heads via body[:-1] for every snake. So cannot move into any current head. Is that correct? After movement, current head becomes body neck for that snake, yes. But what if that snake length 1? not. What if that snake dies this turn by moving out? It still had body during collision? Death and our collision same elimination; if it dies by wall, body disappears immediately in step4 simultaneous. If we move into its old head, after movement its body still includes old head until elimination; but if it dies same step, does it disappear before our body collision? Rule lists elimination simultaneously, dead snakes disappear. Typically collision checks all at same time: our head at their body cell; their body exists at start of elimination. Even if their head goes out, their body remains? They die and disappear maybe same instant. Ambiguous. Conservative avoid.

But current head cell after movement becomes neck only if snake moves. It must move unless blocked? It always moves selected direction, even if into body dies, body still moved? If it dies before? Simultaneous. Anyway avoid.

Head-on contest with target not in occ. Opp current head cannot move into our target if target in occ? no.
Opponent possible moves record filter `if (ox,oy) in occ_set: continue`. But for op, if it moves into our current tail unique, occ excludes, safe. If op target equals our newhead, not in occ. Good.

Starvation: The bot's my_health maybe >1. In candidate, if health_after<=0 and not grow invalid. If health_after==0 but grow True health set100, fine. If health_after is 0 from health=1 and no grow, invalid. If health=0 (should not alive), any no grow invalid.

Direction return: chosen vec name. If chosen candidate actual move vec. We generated legal_moves(cur); cur = infer_dir(my_body). This excludes reverse. But what if body all duplicates at spawn, cur None -> all directions. Good.
If no candidates due all invalid, fallback:
  # generate all actual moves from cur, including those out/body, choose one that is in bounds and maybe not occ; if none body safe, choose one with maximum "free neighbor ignoring body" but avoid reverse.
  moves = legal_moves(cur)
  best=None; bestscore=-1e9
  for vec in moves:
    tx=head+...
    if out: continue
    # score = -100000 if in occ_set else 0 + count free neighbors in bounds not occ_set
    sc=0
    if (tx,ty) in occ_set: sc-=10000
    # count out? 
    # count cells around target in bounds not occ
    for d in DIR_VECS:
      nx=tx+d[0]; ny=ty+d[1]
      if 0<=... and (nx,ny) not in occ_set: sc+=1
    # prefer near food
    if (tx,ty) in food_set: sc+=5
    if sc>bestscore: bestscore=sc; best=vec
  if best is None:
     # choose current dir if in bounds? or any
     best=moves[0]
  return DIR_NAMES.get(best, "up")
Need handle cur None and no in-bound? board always.

Potential issue: legal_moves(cur) returns perpendicular using formula but order; if cur is e.g. (0,-1), p1=(1,0), p2=(-1,0). Good. No reverse.
If current direction inferred but body has duplicate near head and first distinct may be more than one step away. Sign okay. Opposite current invalid rule based actual last direction, which may not be exactly head - first distinct if multiple duplicates? Suppose spawn body all same then moves right. After first move? Body may be [5,5],[5,5],[5,5]? At turn 1 no cur. If choose right, new head 6,5, body after move [6,5],[5,5],[5,5] (remove last duplicate? old body[:-1]=[5,5],[5,5]? body [6,5],[5,5],[5,5]). Last two duplicate; current dir can infer first distinct at index1: head (6,5)- (5,5) = right. Good.
If body [H, H, neck]? Could first distinct two steps behind if neck duplicate? Example after growth at head? Growth at tail only, so head duplicates only spawn. After first move, head unique. So infer okay.

Scoring and search weights need tune. Let's think of risk. If target is possible longer head, score -4000. This may cause bot to avoid even if opponent won't choose, leading safe. In multi, many possible cells, maybe too conservative; but survival priority. If all moves within reach of heads, choose least risk + area.
If equal length, both die if collide. Avoid.

However, if target equals an opponent's possible move but opponent longer, and that opponent might be forced or choose food, avoid. If target has food, both grow; still if op len_after>=our new_len risk. If we are one longer, we survive. But if same cell and we are longer, we kill them and survive; bonus. Our risk condition only risk if op_len_after >= ours. Good.

Could intentionally attack shorter by moving into their possible head. But if they don't move there, no effect. Aggression bonus small.

Search uses current food_mask after candidate. For candidate grow true, remove that food. For search, future foods only remaining current foods; no new food spawning. In real, food eaten respawns, but within horizon maybe not. For long search, absence of respawn underestimates future food. But horizon small. Could include all initial foods not eaten? If we eat, there will be a new food somewhere random; unknown. Search removing eaten means fewer foods and may underweight aggressive eating? Immediate grow gets reward; okay. For future after eating, there should still be same count food (respawn) but unknown; ignoring may slightly reduce search score. Not critical.

Need ensure beam_search performance and correctness with `other_blocked_bool` when passed to `bytearray(other_blocked_bool)`: bytearray copy works. In code, if other_blocked_bool is bytearray. Yes.

Potential optimization: In search, checking self collision by iterating b indices each move. Use `if (tx,ty) in b[:-1]` simpler. Body length up to maybe 100; expansions ~1000, fine. Use `target = (tx,ty); if target in b[:-1]: continue`. Slicing creates tuple each move. Could use `if target in b[:-1]`. Acceptable.
Mobility `if (nx,ny) not in nb[1:]` slices each dvec; better build `nb_set = set(nb[1:])`. For each expansion, create set. Body length small. Use:
   occupied_self = set(nb[1:])  # for mobility? Also not for legal next step because tail may vacate. For mobility rough.
   for dvec... if (nx,ny) not in other_blocked_set and (nx,ny) not in occupied_self: mob+=1
Could compute nb_set once. Fine.
For self collision, we can check loop with b_set? Need allow tail. Use `target in b[:-1]` directly.

Beam dedup: Not necessary. But expanded sorted and top beamw. Could duplicate states. Fine.

Depth/width adaptive:
N=W*H
if state["num_snakes"] <=2:
    depth=10; beamw=12
else:
    depth=7; beamw=10
Maybe for 31x31 multi, N large. Time still okay. 4 candidates * depth*beam*branch ~4*7*10*3=840 expansions. Each expansion nearest food iterates up to12, mobility 4, body check length. Very fast. The final BFS per state: states up to beamw after depth or if no expansion. 4*10 BFS * N(961)=38k. Good. Could use depth=10 for multi too; 4*10*12*3=1440 expansions. Fine. Let's use depth=8 multi, 12 duel. Time safe.
Candidate BFS per 4 candidates each full N=961 level using modulo per node ~4*961=3844. Trivial. Search final 40*961=38k. All under 50ms? Python 50ms perhaps 38k+expansions, yes. 800 turns => 30M operations maybe okay. Per turn 50ms CPU, plenty.

Actually `bfs_metrics` uses level BFS with list allocations; 4 candidates. Fine.

Potential bug in `bfs_metrics` food check `idx in food_idx_set` inside BFS, membership set O(1). Good.
Need count free neighbors function:
def count_free_neighbors(idx, blocked_bool, W,H,N):
  cnt=0
  if idx>=W and not blocked_bool[idx-W]: cnt+=1
  if idx<N-W and not blocked_bool[idx+W]: cnt+=1
  if idx%W!=0 and not blocked_bool[idx-1]: cnt+=1
  if idx%W!=W-1 and not blocked_bool[idx+1]: cnt+=1
  return cnt
Use blocked_bool occ_bool. For target itself not blocked. If target at old head of other? target legal not occ, so not blocked.

Potential issue: occ_bool marks current heads. For flood from candidate, includes current heads as obstacle. But after movement, current heads remain as necks, so yes. However current heads of snakes that die? ignore.

Calculate `my_length`: Use s["length"] but body length maybe. For head-on after grow use len(new_body). Opp length after use s["length"] + grow. State "length" maybe includes duplicates; len(body) likely same. To be consistent, use `len(s["body"])` for all? Example state length=4, body len4. Use given length safer? If overlapping tail duplicate counts as length? Body list contains duplicates and length=4. len same. Use `s.get("length", len(body))`.
For my new_body grow length len(new_body). Opp olen given. If duplicate count same. Use `int(s.get("length", len(s["body"])))`.

Potential issue: Health after candidate. We calculate `health_after = 100 if grow else my_health - 1`. If my_health=0? skip. Good.

Search health: uses h after first move. Candidate already computed. In beam, for next moves health decrements; if h=1 and no food, invalid (dies). If h=0 shouldn't.

Now let's think about strategy and scoring with area. If bot is longer, maybe should seek head collisions with shorter. But primary survival. In multi, length at end matters; need eat. Our score length*25 makes food important. Area*4 makes open. Risk huge. Search adds future area*2.5. Should be okay.

Could include opponent body avoidance in search static. But other snakes move; static may block food route. If a food is behind an opponent's body that will move, search may avoid. But initial candidate scoring includes current body. Fine.

Could there be an issue with candidate target in `occ_set` excludes other snake current unique tail. But if that other snake eats this turn, its tail will still vacate then new duplicate at previous tail? We reasoned old unique tail vacates regardless. If the snake eats, body after move = [newhead]+body[:-1]+copy(body[-2]); current tail body[-1] removed; copy body[-2], not old tail. So old tail cell vacated. Safe. Good.
If another snake's current tail is duplicate, body[:-1] includes one duplicate; occ_set includes coordinate; target deadly. During movement, one duplicate removed; the other remains at tail? Body [H,A,T,T], remove last T -> [H,A,T], so T remains. Yes deadly.

What about target equals other snake current head when other snake length 1? no.

Could our candidate target be occupied by food and by current unique tail of another? Food always empty, so no.

Now code. Need include only code block and short description after. User says "回复里只放一个 ```python 代码块，里面是完整 bot.py。代码块后面用不超过300字简述". We'll provide code block and a brief Chinese paragraph.

Let's write code carefully.

Implementation details:

```
DIRS = [(0,-1),(1,0),(0,1),(-1,0)]? Need include up,down,left,right. Let's define actual all four maybe order.
DIR_VECS = [(0,-1),(1,0),(0,1),(-1,0)] # up,right,down,left
DIR_NAMES = {(0,-1):"up",(1,0):"right",(0,1):"down",(-1,0):"left"}
```
Order no matter.
infer_dir sign.

Function legal_moves(cur):
```
if cur is None: return DIR_VECS
res=[cur]
dx,dy=cur
p1=(-dy, dx)
p2=(dy, -dx)
if p1 != cur and p1 not in res: res.append(p1)
...
```
For cur, p may duplicate? dx,dy unit, no.
Perpendiculars both valid.

In decide, me = None:
```
for s in state["snakes"]:
   if s["id"]==you: me=s; break
if me is None: return "up" maybe
```
Body may be list of lists. Copy:
```
my_body = [(int(p[0]), int(p[1])) for p in me["body"]]
```
Snakes body similarly maybe convert? For coordinate set, use tuple(seg[0],seg[1]).
We don't mutate state.

Build occ_set:
```
occ_set=set()
for s in snakes:
   b=s["body"]
   if len(b)<=1:
      # After move, if length1 no body old? min3
      pass
   for i in range(len(b)-1):
      occ_set.add((b[i][0], b[i][1]))
```
Using body[:-1]. For len1, no occupied after? But if a snake length1, its head moves and old head vacates? Actually length1: move head, then remove tail same cell? Movement simultaneous: old head? If length1, tail shrinks? Rules length starts3. Ignore. But for correctness, body[:-1] empty. Then other can move into old head. Fine.
occ_bool mark each coord:
```
occ_bool=bytearray(N)
for x,y in occ_set: occ_bool[y*W+x]=1
```
If duplicate fine.

food:
```
food_coords=[(int(f[0]), int(f[1])) for f in state["food"]]
food_set=set(food_coords)
food_mask=0
food_idx_set=set()
for x,y in food_coords:
  idx=y*W+x; food_mask |= 1<<idx; food_idx_set.add(idx)
```
Potential foods not in bounds? assume.

other_blocked_set & bool:
```
other_set=set()
for s in snakes:
  if s["id"]==you: continue
  b=s["body"]
  for i in range(len(b)-1):
      other_set.add((b[i][0], b[i][1]))
other_bool=bytearray(N)
for x,y in other_set: other_bool[y*W+x]=1
```
If other_set includes current heads, yes.

cur = infer_dir(my_body)
moves = legal_moves(cur)

Depth:
```
if state["num_snakes"] <= 2:
    depth=12; beamw=12
else:
    depth=9; beamw=10
```
May be too high? 4*12*12*3=1728 expansions. Fine.

For each vec in moves:
  tx,ty = head+vec
  if out continue
  target=(tx,ty)
  if target in occ_set: continue
  grow = target in food_set
  health_after=100 if grow else my_health-1
  if (not grow) and health_after<=0: continue
  # build new_body
  nb_list = [target] + my_body[:-1]
  if grow: nb_list.append(nb_list[-1])
  new_len = len(nb_list)  # or my_length + grow
  # But if my_body may have duplicate tail and no grow, new_len = len(my_body) (because [target]+body[:-1] length same as len(body)). If grow +1.
  # Compute risk
  risk=0; aggr=0
  for (rx,ry,olen,oid) in op_records:
      if rx==tx and ry==ty:
         olen_after = olen + (1 if target in food_set else 0)  # if grow defined target food same
         if olen_after >= new_len: risk +=1
         else: aggr +=1
  score = ...
```
Need `op_records` precompute before candidate. Let's do:
```
op_records=[]
for s in snakes:
   if s["id"]==you: continue
   b=s["body"]; if not b: continue
   oh=(b[0][0],b[0][1])
   ocur=infer_dir(b)
   omoves=legal_moves(ocur)
   olen=int(s.get("length", len(b)))
   for ov in omoves:
      ox=oh[0]+ov[0]; oy=oh[1]+ov[1]
      if ox<0 or ox>=W or oy<0 or oy>=H: continue
      if (ox,oy) in occ_set: continue
      op_records.append((ox,oy,olen,s["id"]))
```
Note occ_set includes unique tail excluded. If opponent could move into our candidate target which is a unique tail, not in occ, record. Good.
But `legal_moves(ocur)` excludes reverse. Good. If op has no dir (spawn), all four. If body has duplicate and current direction unknown maybe all.
Some op moves may be invalid due starvation. Ignore.

For candidate, if op target equals target multiple times same op? moves unique, no.

Score:
```
score = new_len * 25.0
if grow: score += 180.0
score += max(0, health_after)*0.4
score -= risk * 5000.0
score += aggr * 35.0
# area
area, fdist = bfs_metrics(y*W+x, occ_bool, food_idx_set, W,H,N)
mob = count_free_neighbors(...)
score += min(area, 180)*4.0
score += mob*10.0
need = new_len + 2
if area < need: score -= (need-area)*180.0
if fdist < 999:
   if health_after < 25: score += max(0, 350 - fdist*35)
   elif health_after < 55: score += max(0,180 - fdist*15)
   else: score += max(0,80 - fdist*8)
else:
   if health_after < 70: score -= 250
if health_after < 20: score -= 150
# proximity
for s in snakes:
   if s["id"]==you: continue
   ob=s["body"]; if not ob: continue
   ox,oy=ob[0]
   d=abs(tx-ox)+abs(ty-oy)
   slen=int(s.get("length", len(ob)))
   if slen >= new_len:
      if d==1: score -= 130
      elif d==2: score -= 30
      elif d==3: score -= 6
   else:
      if d==1: score += 12
# edge
edge=min(tx,ty,W-1-tx,H-1-ty)
score += edge*1.5
# future
mask_after = food_mask & ~(1<<(ty*W+tx)) if grow else food_mask
search_val = beam_search(nb_list, health_after, mask_after, vec, other_set, other_bool, W,H,N, food_coords, depth, beamw)
score += search_val
```
Potential double count health etc. Fine.
Store best_score, best_vec, best_details. If risk huge, might choose no risky. If all risk, choose least.

Question: In search, we pass `nb_list` which is list of tuples. If grow and nb_list[-1] duplicate. Good.
`health_after` already after first move. Search then simulates future; it may decrement and if no food with health<=1 invalid. Good.

BFS metrics uses occ_bool which includes our current body excluding tail. For candidate target that is current unique tail, occ_bool doesn't include, BFS can start there. It also doesn't include our new body's shifted segments except old body[:-1] (occ). That's same as new_body[1:] except if grow appends duplicate at tail (same cell already in occ? Let's check: old body [H,A,T]. occ includes H,A. new_body grow [target,H,A,A]; blocked should include H,A,A (A duplicate). occ includes H,A (A already). So no missing. If no grow new_body [target,H,A]; blocked H,A = occ. So occ_bool exactly equals all new body excluding new head for our snake, plus old bodies for others. It also includes other current heads/necks. Great. It does not include our candidate target, so BFS from target through free cells treats our own body blocked. Good. If we eat and append duplicate of A, already blocked A one copy; duplicate no new cell. So okay. Thus area is accurate for immediate next with others static.

Search static other_bool excludes my entire initial body, but search dynamic b includes body. For future BFS, blocked = other_bool + b[1:] (all own body except head) includes current tail too, whereas tail may vacate next move. Conservative. Fine.

`bfs_metrics` need N passed. Use `idx % W` many. Let's code:
```
def bfs_metrics(start, blocked, food_idx, W,H,N):
    seen=bytearray(N)
    if start<0 or start>=N or blocked[start]:
       return 0,999
    seen[start]=1
    q=[start]; qi=0; dist=0; minfood=999; area=0
    # To process levels, use q with distances? Easier use q and a parallel dist array? Use level.
    current=[start]
    while current:
       nxt=[]
       for idx in current:
          area+=1
          if idx in food_idx and dist<minfood: minfood=dist
          if idx>=W:
             n=idx-W
             if not seen[n] and not blocked[n]: seen[n]=1; nxt.append(n)
          if idx<N-W:
             n=idx+W
             if not seen[n] and not blocked[n]: seen[n]=1; nxt.append(n)
          if idx%W:
             n=idx-1
             if not seen[n] and not blocked[n]: seen[n]=1; nxt.append(n)
          if idx%W != W-1:
             n=idx+1
             if not seen[n] and not blocked[n]: seen[n]=1; nxt.append(n)
       current=nxt; dist+=1
    return area,minfood
```
Note `if idx%W` for left; for right `idx%W != W-1`. Good. For N-W when N=W*H. Down condition idx < N-W. Good.
If start blocked due candidate? shouldn't. But if target is unique tail and occ_bool not blocked. okay.

`count_free_neighbors` similar.

Beam search code careful with variable names.

```
def beam_search(body_list, health, food_mask, cur_vec, other_blocked, other_blocked_bool, W,H,N, food_coords, depth, beamw):
    b0=tuple(body_list)
    states=[(b0, health, food_mask, cur_vec, 0.0)]
    for step in range(depth):
        expanded=[]
        for b,h,mask,cur,acc in states:
            head=b[0]
            for vec in legal_moves(cur):
                tx=head[0]+vec[0]; ty=head[1]+vec[1]
                if tx<0 or tx>=W or ty<0 or ty>=H: continue
                if (tx,ty) in other_blocked: continue
                # self collision against b[:-1]
                bad=False
                # b[:-1] excludes last segment
                for i in range(len(b)-1):
                    if b[i]==(tx,ty):
                       bad=True; break
                if bad: continue
                idx=ty*W+tx
                grow = (mask >> idx) & 1
                if grow:
                    nh=100
                else:
                    nh=h-1
                    if nh<=0: continue
                nb_list=[(tx,ty)]
                nb_list.extend(b[:-1])
                if grow:
                    nb_list.append(nb_list[-1])
                nb=tuple(nb_list)
                nmask = mask & ~(1<<idx) if grow else mask
                # mobility
                mob=0
                # use set of nb[1:]
                # for d in DIR_VECS:
                #   nx...
                # self set maybe:
                selfset=set(nb[1:])
                for dvec in DIR_VECS:
                   nx=tx+dvec[0]; ny=ty+dvec[1]
                   if 0<=nx<W and 0<=ny<H and (nx,ny) not in other_blocked and (nx,ny) not in selfset:
                      mob += 1
                mind=999
                for fc in food_coords:
                    cx,cy=fc
                    bidx=cy*W+cx
                    if (nmask >> bidx) & 1:
                       d=abs(tx-cx)+abs(ty-cy)
                       if d<mind: mind=d
                acc2=acc + 1.0
                if grow:
                    acc2 += 45.0
                    if h<70: acc2 += (100-h)*0.15
                hval=acc2 + len(nb)*1.5 + mob*4.0 + nh*0.05
                if mind<999:
                   hval -= mind*(4.0 if nh<50 else 2.0)
                if mob==0: hval -= 100.0
                expanded.append((hval,nb,nh,nmask,vec,acc2))
        if not expanded: break
        expanded.sort(key=lambda z:z[0], reverse=True)
        states=[]
        for hval,nb,nh,nmask,vec,acc2 in expanded[:beamw]:
             states.append((nb,nh,nmask,vec,acc2))
    best=-1e18
    for b,h,mask,cur,acc in states:
        blocked=bytearray(other_blocked_bool)  # copy
        for seg in b[1:]:
            blocked[seg[1]*W+seg[0]]=1
        start=b[0][1]*W+b[0][0]
        if blocked[start]:
            area=0
        else:
            seen=bytearray(N)
            q=[start]; seen[start]=1; qi=0; area=0
            while qi < len(q):
                idx=q[qi]; qi+=1; area+=1
                if idx>=W:
                    n=idx-W
                    if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
                if idx<N-W:
                    n=idx+W
                    if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
                if idx%W:
                    n=idx-1
                    if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
                if idx%W != W-1:
                    n=idx+1
                    if not seen[n] and not blocked[n]: seen[n]=1; q.append(n)
        val = acc + area*2.5 + len(b)*6.0 + h*0.1
        if val>best: best=val
    return best
```
Potential bug: `mask & ~(1<<idx)` in Python negative bit works because mask positive and ~ negative, but `mask & ~(1<<idx)` clears bit correctly. Fine.
`grow` is int 0/1. Use bool? if mask bit.
`legal_moves(cur)` returns list containing cur and perpendiculars. In search, cur_vec passed from first move. Good.
`other_blocked_bool` is bytearray. `bytearray(other_blocked_bool)` works.

One performance concern: In beam search, for each expansion `selfset=set(nb[1:])`; body length may grow large (up to maybe 100), but expansions ~1000, okay.
`food_coords` iteration and shifting per food per expansion. Up to12*1000=12k, fine.
States len can be less than beam if no expansion.

Now candidate scoring risk: op_records uses `occ_set` which includes current bodies but not target if current unique tail. For op safe moves, if op target is a current body of a snake that will move its head away? Wait `occ_set` includes all body[:-1], i.e., all positions that remain after movement for each snake excluding unique tails. It includes current heads. Suppose opponent op wants to move into another snake's current head cell. After movement, that cell becomes neck (body), so op would die. Filtered. Correct. If op target is another snake's current unique tail, excluded from occ_set, so considered safe. After movement that tail vacates, safe unless head-head with us. Correct. Good.

For candidate legal, `if target in occ_set: continue`. This treats current heads deadly. Correct as reasoned. Let's double-check with simple two snakes head-to-head in same cell current? If two current heads adjacent, moving into each other's current head: Target = opponent's current head. occ_set includes opponent current head (because body[:-1] includes index0). We deem invalid; indeed if both move, our head would go into their old head, which becomes their neck. But what if they also move into our old head, head-swap? After movement, our head at their old head; their newhead at our old head. Their old head is occupied by their neck (body), so we collide with their body and die. Their newhead collides with our neck? We die too. So invalid correct. The only way target equals opponent current head safe is if opponent length1 and old head vacates without body; min3 no.

What about target equals our own current tail unique. occ_set excludes. After movement, our new body [tail,H,A]. Our head at old tail, old tail removed. Safe if follows tail. Good.
What if target equals our own current tail duplicate. occ_set includes duplicate (body[:-1] contains T). Invalid. Correct.

Now consider candidate target being a food cell on our own unique tail? impossible.

Now fallback code. We need if best_vec None. Use moves = legal_moves(cur); if cur None moves all. Choose:
```
best_vec=None; best_sc=-1e18
for vec in moves:
  tx...
  if out: continue
  sc=0
  if (tx,ty) in occ_set: sc-=100000
  # free neighbors in bounds not occ
  for d in DIR_VECS:...
  if (tx,ty) in food_set: sc+=1000
  # prefer current? no
  if sc>best_sc: ...
if best_vec is None:
  # choose cur if not None else (0,-1)
  if cur is not None: best_vec=cur
  else: best_vec=(0,-1)
```
Return name. If best_vec corresponds actual move. If cur None and chooses a direction from moves. If best_vec chosen current direction due invalid reverse? legal_moves actual. Good.

Potential issue: `legal_moves(cur)` if cur None returns `DIR_VECS` global list. We don't mutate. Good.

Let's craft final code with functions outside decide. Module globals. No random needed.

Test mentally on example state:
snakes id0, id1; my body. infer dir. occ_set includes indices0..len-2 for all, including heads. Candidate moves not into body except tails.
Suppose my head (9,3), body (9,4),(9,5),(9,5). Current dir from head - (9,4) = (0,-1) up. legal moves [up, right? dx=0,dy=-1; p1=(1,0), p2=(-1,0)] => up,right,left. It cannot go down reverse.
If me health100. Good.
New body no grow [target]+my_body[:-1]. It removes last duplicate? my_body [9,3],[9,4],[9,5],[9,5], body[:-1]=first3; if move up to 9,2 -> [9,2],[9,3],[9,4],[9,5] (one duplicate removed). Correct.

Now could candidate target equal current tail duplicate (9,5)? occ_set includes body[:-1]=[9,3],[9,4],[9,5] (indices0-2), so (9,5) in occ, invalid. Correct because tail duplicate remains.

If body unique [9,3],[9,4],[9,5], occ_set includes [9,3],[9,4], excludes (9,5). A move down into (9,5) would be reverse (current up) so not generated. If cur none maybe could. Safe follow tail.

Now scoring risk uses `new_len = len(nb_list)`. For no grow with duplicate tail removed length same? my_body length4 -> nb length 4 (target + 3). State length maybe4. okay. If grow ->5.
Opp length after = olen + (1 if target in food_set else0). If target food, both eat. If opponent might not be able to eat because their target same and food maybe eaten, rule both count. good.

Now one subtlety: Head-on collision after eat: If our new head enters opponent's current body neck (occ_set), we die by body before head-head. We invalid. If target equals opponent possible new head but not current body, occ_set doesn't contain. risk. After movement, if opponent also moves there, head-head. What if target is occupied by food; both eat and grow. use new_len and olen_after. Good.
If multiple opp possible same target with one longer, risk. We penalize per record. If one equal, both die if contest. If unique longer opponent, we die, they survive. If we are longer than all, aggr. If there is a record equal and another we longer, risk. Good.

Now scoring search: It may choose routes through cells that are possible opponent head cells in future, but no danger. However initial risk handles immediate. Could add danger penalty in beam h for cells within Manhattan1 of longer opponent heads static. But other heads move. Maybe not.

Maybe in multi, avoiding occupied body but not other heads for future can lead into a head-on next turn. But because search states are hypothetical for our snake, it doesn't know opponents. Initial candidate only. At next decide, actual state updates and risk recalculated. The bot can react every turn. So okay.

We should ensure decide returns quickly. `op_records` only computed once. Beam_search called per candidate (up to 3) not 4 because no reverse. In spawn no cur all4. Depth 12 duel, width12. For 3 candidates ~3*12*12*3=1296 expansions, final BFS 3*12*961=34k. Fine.

Let's write final code now.

Wait: In `legal_moves(cur)`, if cur is None returns DIR_VECS, which is list of tuples. In beam search, if cur passed as vec known. At spawn initial cur None, candidate vec selected. Search cur_vec=vec. Good. For opponent possible moves, if op current None all four.

`infer_dir` sign for dx>0 first. If body[1] not adjacent but same row with dx=2 due spawn duplicates? It returns (1,0) based sign. Good.

Potential bug: `state["num_snakes"]` available. yes.

Now final code. Let's include no print.

Need maybe reset module globals between games? Functions no persistent global state except DIRS. Fine.

Let's produce final.