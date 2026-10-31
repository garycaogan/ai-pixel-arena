We need fix timeouts. Need understand cause: our time checks too sparse (every 128 nodes) and expensive flood fill / evaluate maybe overshoots. 797ms max suggests huge overshoots due time checks not called in region_food? check_time called in policy detailed per candidate, but evaluation calls region_food directly without check_time inside loop, cap up to 180 area maybe fine, but search deep with many nodes, check every 128 nodes but each node can be expensive, especially next_state with many snakes/body masks repeated. Need robust timing: budget lower, check every 8 nodes, check inside region_food maybe every 16 cells. Reduce search depths and candidate expansions. Also setup? first turn 797 maybe load? It says single turn max 797.51 CPU, perhaps turn 1 due too deep search and missed checks. Need optimize aggressively. Since self-check errors only timeouts, goal pass. Could simplify: keep search but stricter budget and node checks.

Time accounting: DEADLINE start + 0.038; but if start function overhead and checks sparse, overshoot. Use budget 0.020 for after first? Need account judge CPU same process. choose 0.022. First 0.55.

Need make check_time every 8 or 16. But frequent time.process_time calls cost; every 16 okay. Add checks in region_food each cell iteration maybe global counter; since function called often, use check_time at function entry and in while loops every? easiest call check_time() in region_food for each expanded cell? too costly but okay? Let's increment NODES and check time every 16 expansions. But NODES also used search nodes. Fine.

BODY_MASKS caching with keys containing tuples and mode. next_state computes segmask body_mask for every record and board body masks. In 11 snakes, expensive but okay. Search maybe huge. Brawl depth 3 root candidates up to 4, each child brawl_search enumerates own actions 4 and next_state with 11 snakes, then depth2 etc => ~4*4*4=64 states each with enemy plans policy per snake at each node: expensive. maxdepth after first is 3, but iterative starts depth1,2,3. Probably can still be heavy; reduce after first maxdepth=2 for brawl? Maybe use depth1 root + depth? Brawl root values with scenarios, each candidate up to 1+3 scenarios = 4*4=16 next_states, then brawl_search depth2 for each -> each 4 own moves with next_state => 64 more next states. heavy. Could lower to depth=2 only. Duel depth 5 maybe okay on 15x15 but flood fills expensive. Reduce to depth 4 after first, 6 first.

Better root candidate filtering: CANDIDATE_ORDER only min immediate risk candidates, often all 3. okay.

Need ensure worst-case under 50. Could implement hard node limit e.g. 12000? Time checks enough.

Main issue maybe SearchTimeout raised inside time check only every 128; a single evaluate can exceed 50 due region_food cap 180 and body masks? 797ms indicates many evaluates between checks. Check every 8.

Also EVAL_CACHE key st includes tuples; fine.

Potential recursion duplicate states causing lots.

Let's produce revised code with:
- DEADLINE start + (0.60 if turn1 else 0.020)
- check_time: NODES +=1; if (NODES & 7)==0...
- in region_food: while q: check_time() maybe every layer; inner expansion call check_time maybe every 8 using global; easiest at start of for c? call check_time() each cell might cost but cells <=225/961, okay but time.process_time every 8. Use check_time() call itself increments. That makes region expansion counted. At while q layer call check_time; inside for n maybe not. A layer could expand many cells; max 961 but checks per layer only could overshoot ~ maybe flood fill 961 bit ops <1ms. okay. But evaluates many; check each function entry and each while layer.
- policy detailed calls region for each action; okay.
- duel_values enemy policy detailed=True causing up to 4 region_food for enemy plus evaluations; okay.
- reduce depths: duel maxdepth = 5 first else 4; brawl 3 first else 2. Could even brawl 2 always. First turn 1 sec but keep 3.
- In brawl_values scenarios max maybe candidates*4 = 16; depth2 child search. okay.
- Add a root time fallback in loops: check before each candidate.
- maybe skip detailed policy in enemy_plan for brawl root: policy_actions(..., detailed=True) for every enemy (up to 10) each root -> each up to 4 actions flood fill = 40 region_food; costly. Change to detailed=False for baseplan; only near_options use detailed=True for up to 3 enemies. That greatly helps. policy detailed for enemy plans unnecessary.
- enemy_plan during brawl_search uses detailed=False already.
- region cap in brawl eval min(180,length*3) -> reduce to 120. Duel 60 okay. Use cap min(AREA-1, max(50,min(120,...)))
- MAX nodes maybe if NODES > 200000 raise timeout? not needed.

Also first turn deadline 0.78 but max turn was 797: likely first turn. set 0.55.

Need provide full code. Ensure no accidental issue. Could retain logic. Let's rewrite with modifications. Must only code block + <=300 words. Need be careful syntax.

One subtlety: check_time uses global NODES; region_food calls check_time frequently causing NODES huge and process_time every 8; overhead modest. Good.

Set DEADLINE = start + (0.55 if turn<=1 else 0.022). CPU overhead before start minimal. 22ms leaves margin. In competition 50ms CPU; 22 conservative may weaken but pass. Maybe 0.030. Use 0.030? Since checks frequent, overshoot small. Use 0.030 after first, 0.65 first. Self-check strict. 30ms safe. First 0.75.

Need include time import etc.

Let's ensure duel_values for depth uses duel_search(ns, depth-1, best, INF). alpha=best; if best=-INF okay. In duel_search, for each own action it loops enemy actions, breaks if worst <= alpha. For subsequent own actions alpha=best. fine.

Potential bug BODY_MASKS keys with tuples large memory but clears.

Final answer code.