from math import sqrt
from time import process_time as _clock


_NAMES = ("up", "down", "left", "right")
_BOARDS = {}
_target = None
_last_direction = "up"
_backup = "up"


class _TimeUp(Exception):
    pass


class _Board:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.size = width * height
        self.full = (1 << self.size) - 1
        self.bits = tuple(1 << p for p in range(self.size))
        self.x = tuple(p % width for p in range(self.size))
        self.y = tuple(p // width for p in range(self.size))
        self.neighbors = []
        self.adjacent = []
        self.edge = []
        self.center = []
        left = right = 0
        for y in range(height):
            left |= self.bits[y * width]
            right |= self.bits[y * width + width - 1]
        self.not_left = self.full ^ left
        self.not_right = self.full ^ right
        for p in range(self.size):
            x, y = self.x[p], self.y[p]
            choices = []
            if y:
                choices.append((p - width, 0))
            if y + 1 < height:
                choices.append((p + width, 1))
            if x:
                choices.append((p - 1, 2))
            if x + 1 < width:
                choices.append((p + 1, 3))
            self.neighbors.append(tuple(choices))
            mask = 0
            for q, _ in choices:
                mask |= self.bits[q]
            self.adjacent.append(mask)
            self.edge.append(min(x, y, width - 1 - x, height - 1 - y))
            self.center.append(abs(2 * x - width + 1) +
                               abs(2 * y - height + 1))

    def expand(self, mask):
        return (((mask & self.not_right) << 1) |
                ((mask & self.not_left) >> 1) |
                (mask << self.w) | (mask >> self.w)) & self.full

    def room(self, seed, blocked, cap=0):
        allowed = self.full & ~blocked
        seen = frontier = seed
        while frontier:
            if cap and seen.bit_count() >= cap:
                break
            frontier = self.expand(frontier) & allowed & ~seen
            seen |= frontier
        return seen


def _trim(snake, board):
    body, _, occupied = snake
    if len(body) > 1 and body[-1] == body[-2]:
        return occupied
    return occupied & ~board.bits[body[-1]]


def _advance(snake, destination, food, board):
    body, health, _ = snake
    bit = board.bits[destination]
    ate = bool(food & bit)
    new_body = (destination,) + body[:-1]
    if ate:
        new_body += (new_body[-1],)
    return (new_body, 100 if ate else health - 1,
            _trim(snake, board) | bit)


def _schedule(board, snakes, horizon, delays=None):
    release = [0] * board.size
    for index, snake in enumerate(snakes):
        body = snake[0]
        delay = bool(delays and delays[index])
        length = len(body)
        for j, p in enumerate(body):
            t = length - j
            if delay and t > 1:
                t += 1
            if t > release[p]:
                release[p] = t
    buckets = [0] * (horizon + 1)
    occupied = 0
    for p, t in enumerate(release):
        if t:
            bit = board.bits[p]
            occupied |= bit
            if t <= horizon:
                buckets[t] |= bit
    result = [occupied]
    for t in range(1, horizon + 1):
        occupied &= ~buckets[t]
        result.append(occupied)
    return result


def _distance(board, a, b):
    return abs(board.x[a] - board.x[b]) + abs(board.y[a] - board.y[b])


def _nearest(board, head, foods):
    if not foods:
        return 0
    x, y = board.x[head], board.y[head]
    best = 10000
    for f in foods:
        d = abs(x - board.x[f]) + abs(y - board.y[f])
        if d < best:
            best = d
    return best


class _Enemy:
    pass


class _Game:
    def __init__(self, state, started):
        key = (state["width"], state["height"])
        board = _BOARDS.get(key)
        if board is None:
            board = _Board(*key)
            _BOARDS[key] = board
        self.b = board
        self.started = started
        self.deadline = started + 0.039
        self.remaining = max(
            1, state.get("max_turns", 800) - state.get("turn", 1) + 1
        )
        own_id = state["you"]
        raw_me = next(s for s in state["snakes"] if s["id"] == own_id)
        raw = [raw_me] + [
            s for s in state["snakes"] if s["id"] != own_id
        ]
        snakes = []
        for s in raw:
            body = tuple(y * board.w + x for x, y in s["body"])
            occupied = 0
            for p in body:
                occupied |= board.bits[p]
            snakes.append((body, int(s["health"]), occupied))
        self.snakes = tuple(snakes)
        self.me = snakes[0]
        self.length = len(self.me[0])
        self.health = self.me[1]
        self.head = self.me[0][0]
        self.food = 0
        for x, y in state["food"]:
            self.food |= board.bits[y * board.w + x]
        self.food_cache = {0: ()}
        self.food_points = self.foods(self.food)
        self.initial_block = 0
        for snake in snakes:
            self.initial_block |= _trim(snake, board)
        self.options = []
        for snake in snakes:
            body = snake[0]
            neck = body[1] if len(body) > 1 else -1
            moves = tuple(q for q, _ in board.neighbors[body[0]]
                          if q != neck and
                          not (self.initial_block & board.bits[q]))
            self.options.append(moves)
        self.current_direction = _last_direction
        if len(self.me[0]) > 1:
            delta = self.head - self.me[0][1]
            directions = {-board.w: "up", board.w: "down",
                          -1: "left", 1: "right"}
            self.current_direction = directions.get(
                delta, self.current_direction
            )

    def check(self):
        if _clock() >= self.deadline:
            raise _TimeUp

    def foods(self, mask):
        cached = self.food_cache.get(mask)
        if cached is not None:
            return cached
        original = mask
        result = []
        while mask:
            bit = mask & -mask
            result.append(bit.bit_length() - 1)
            mask ^= bit
        result = tuple(result)
        self.food_cache[original] = result
        return result

    def prepare(self):
        board = self.b
        self.horizon = min(
            96, max(40, board.w + board.h + 6, self.length + 8)
        )
        self.delays = [
            any(self.food & board.bits[q] for q in options)
            for options in self.options[1:]
        ]
        self.foe_blocks = _schedule(
            board, self.snakes[1:], self.horizon, self.delays
        )
        own_blocks = _schedule(board, (self.me,), self.horizon)
        self.all_blocks = [
            a | b for a, b in zip(self.foe_blocks, own_blocks)
        ]
        self.enemy_seen = [0] * (self.horizon + 1)
        self.food_eta = {p: 10000 for p in self.food_points}
        self.enemies = []
        for index, snake in enumerate(self.snakes[1:]):
            self.check()
            enemy = _Enemy()
            enemy.snake = snake
            enemy.length = len(snake[0])
            enemy.head = snake[0][0]
            enemy.options = self.options[index + 1]
            enemy.delay = self.delays[index]
            enemy.eta = {}
            frontier = board.bits[enemy.head]
            seen = frontier
            missing = self.food
            enemy.history = [seen]
            enemy.heads = [frontier, 0, 0, 0, 0]
            self.enemy_seen[0] |= seen
            for t in range(1, self.horizon + 1):
                frontier = board.expand(frontier) & ~self.all_blocks[t]
                hit = frontier & missing
                while hit:
                    bit = hit & -hit
                    p = bit.bit_length() - 1
                    enemy.eta[p] = t
                    if t < self.food_eta[p]:
                        self.food_eta[p] = t
                    hit ^= bit
                    missing ^= bit
                seen |= frontier
                enemy.history.append(seen)
                self.enemy_seen[t] |= seen
                if t <= 4:
                    enemy.heads[t] = frontier
            enemy.first_food = min(enemy.eta.values(), default=10000)
            weights = {}
            for q in enemy.options:
                bit = board.bits[q]
                degree = (board.adjacent[q] &
                          ~self.all_blocks[2]).bit_count()
                d = _nearest(board, q, self.food_points)
                weight = (1.0 + degree * degree) / (1.0 + 0.25 * d)
                if self.food & bit:
                    weight *= 2.0 + max(0, 60 - snake[1]) / 18.0
                elif snake[1] <= 1:
                    weight *= 0.03
                for j, other in enumerate(self.snakes):
                    if j == index + 1:
                        continue
                    if len(other[0]) >= enemy.length and q in self.options[j]:
                        weight *= 0.18
                        break
                weights[q] = max(0.025, weight)
            total = sum(weights.values())
            enemy.probability = (
                {q: w / total for q, w in weights.items()} if total else {}
            )
            self.enemies.append(enemy)


def _root_score(game, root):
    board = game.b
    q, snake = root["q"], root["snake"]
    bit = board.bits[q]
    length, health = len(snake[0]), snake[1]
    ate = bool(game.food & bit)
    no_collision = 1.0
    forced = False
    for enemy in game.enemies:
        if enemy.length >= game.length:
            no_collision *= 1.0 - enemy.probability.get(q, 0.0)
            if enemy.options == (q,):
                forced = True
    collision_probability = 1.0 - no_collision
    block2 = game.foe_blocks[2] | _trim(snake, board)
    next_moves = board.adjacent[q] & ~block2
    if health <= 1:
        next_moves &= game.food
    dangerous = 0
    for enemy in game.enemies:
        if enemy.length + (enemy.first_food <= 2) >= length:
            dangerous |= enemy.heads[2]
    safe_degree = (next_moves & ~dangerous).bit_count()
    area = board.room(bit, block2).bit_count()
    own_blocks = _schedule(board, (snake,), game.horizon)
    frontier = bit
    seen = 0
    territory = 0.0
    food_times = {}
    horizon = min(game.horizon, game.remaining)
    for t in range(1, horizon + 1):
        if not frontier:
            break
        new = frontier & ~seen
        contested = game.enemy_seen[t - 1]
        for enemy in game.enemies:
            if enemy.length + (enemy.first_food <= t) >= length:
                contested |= enemy.history[t]
        territory += ((new & ~contested).bit_count() /
                      (1.0 + 0.08 * (t - 1)))
        hit = new & game.food
        while hit:
            fb = hit & -hit
            food_times[fb.bit_length() - 1] = t
            hit ^= fb
        seen |= frontier
        if t < horizon:
            frontier = (board.expand(frontier) &
                        ~(game.foe_blocks[t + 1] | own_blocks[t]))
        if t & 15 == 0:
            game.check()

    food_weight = 46.0 + 2.2 * max(0, 55 - game.health)
    if (len(game.snakes) == 2 and game.health > 60 and
            game.length > len(game.snakes[1][0]) + 3):
        food_weight *= 0.72
    if game.health > 60:
        food_weight /= 1.0 + max(
            0.0, game.length - 0.28 * board.size
        ) / board.size
    food_value = 0.0
    chosen_food = None
    reliable_distance = 10000
    for f, arrival in food_times.items():
        opponent_arrival = 10000
        opponent_length = 0
        for enemy in game.enemies:
            d = enemy.eta.get(f, 10000)
            potential_length = enemy.length + 1 + (enemy.first_food + 2 <= d)
            if d < opponent_arrival:
                opponent_arrival = d
                opponent_length = potential_length
            elif d == opponent_arrival:
                opponent_length = max(opponent_length, potential_length)
        claim_length = length + (f != q)
        if opponent_arrival < arrival:
            reliability = 0.12
        elif opponent_arrival == arrival and opponent_length >= claim_length:
            reliability = 0.10
        else:
            reliability = 1.0
        distance = arrival - 1
        if reliability >= 0.5:
            reliable_distance = min(reliable_distance, distance)
        value = food_weight * reliability / (arrival + 2.0)
        if f == _target:
            value += 0.35 / (arrival + 1.0)
        if distance > health:
            value *= 0.01
        if value > food_value:
            food_value, chosen_food = value, f

    needed = length + 4
    space_penalty = 0.9 * max(0, needed - area)
    dynamic_area = seen.bit_count()
    if (seen & board.bits[snake[0][-1]]) and dynamic_area >= needed:
        space_penalty *= 0.35
    space_penalty += 6.0 * max(0, length + 2 - dynamic_area)
    if area <= 3 and next_moves.bit_count() <= 1:
        space_penalty += 8.0
    future_weight = min(1.0, max(0, game.remaining - 1) / 7.0)
    value = future_weight * (
        1.6 * sqrt(territory) +
        0.10 * min(area, 2 * length + 24) +
        3.0 * safe_degree - space_penalty
    )
    value += food_value + 8.0 * ate
    value -= 0.35 * max(0, 2 - board.edge[q])
    value -= 0.015 * board.center[q]
    if health < min(35, game.remaining) and reliable_distance > health:
        value -= 80.0 + 5.0 * max(0, min(30, reliable_distance) - health)
    if not next_moves and game.remaining > 1:
        value -= 2500.0

    equal_duel = (len(game.snakes) == 2 and
                  len(game.snakes[1][0]) == game.length)
    if collision_probability > 0:
        if equal_duel:
            value -= 250.0 + 2100.0 * collision_probability
        else:
            value -= 900.0 + 5400.0 * collision_probability
        if forced and not equal_duel:
            value -= 18000.0
    if _NAMES[root["direction"]] == game.current_direction:
        value += 0.12
    root["base"] = value
    root["target"] = chosen_food


def _beam(game, roots, deadline, width):
    board = game.b
    beams = []
    quality = []
    dead = [0] * len(roots)
    for root in roots:
        bit = board.bits[root["q"]]
        food = game.food & ~bit
        gain = 14.0 if game.food & bit else 0.0
        initial_quality = gain - 0.45 * _nearest(
            board, root["q"], game.foods(food)
        )
        beams.append([(root["snake"], food, gain, 0.0, initial_quality)])
        quality.append(initial_quality)

    limit = min(game.remaining, max(14, min(30, game.length + 6)))
    generated = 0
    for depth in range(2, limit + 1):
        if _clock() >= deadline:
            break
        next_beams = []
        next_quality = quality[:]
        next_dead = dead[:]
        try:
            for index, beam in enumerate(beams):
                if _clock() >= deadline:
                    raise _TimeUp
                if not beam:
                    next_beams.append([])
                    continue
                candidates = {}
                for snake, food, gain, risk, _ in beam:
                    blocked = game.foe_blocks[depth] | _trim(snake, board)
                    for q, _ in board.neighbors[snake[0][0]]:
                        bit = board.bits[q]
                        if blocked & bit:
                            continue
                        ate = bool(food & bit)
                        if snake[1] <= 1 and not ate:
                            continue
                        new_snake = _advance(snake, q, food, board)
                        new_food = food & ~bit
                        new_gain = gain
                        if ate:
                            reliability = (
                                0.35 if game.food_eta.get(q, 10000) < depth
                                else 1.0
                            )
                            new_gain += reliability * (
                                16.0 * (0.94 ** depth) +
                                0.10 * max(0, 60 - snake[1])
                            )
                        new_risk = risk
                        if depth <= 4:
                            discount = 0.75 ** (depth - 2)
                            for enemy in game.enemies:
                                possible_length = (
                                    enemy.length + (enemy.first_food <= depth)
                                )
                                if (enemy.heads[depth] & bit and
                                        possible_length >= len(new_snake[0])):
                                    new_risk += 20.0 * discount
                                shadow = 0
                                first = max(1, depth - enemy.length + 1)
                                for earlier in range(first, depth):
                                    shadow |= enemy.heads[earlier]
                                if shadow & bit:
                                    new_risk += 12.0 * discount
                        next_block = (game.foe_blocks[depth + 1] |
                                      _trim(new_snake, board))
                        exits = board.adjacent[q] & ~next_block
                        if new_snake[1] <= 1:
                            exits &= new_food
                        degree = exits.bit_count()
                        cap = min(64, len(new_snake[0]) + 4)
                        room = board.room(bit, next_block, cap).bit_count()
                        distance = _nearest(
                            board, q, game.foods(new_food)
                        )
                        hunger = 0.45 + 0.06 * max(0, 40 - new_snake[1])
                        score = (
                            new_gain - new_risk - hunger * distance +
                            2.0 * degree + 0.20 * min(room, cap) -
                            0.90 * max(0, min(cap, len(new_snake[0]) + 2) - room) -
                            0.20 * (board.edge[q] == 0)
                        )
                        if degree == 0 and depth < game.remaining:
                            score -= 100.0
                        key = (new_snake[0], new_food, new_snake[1])
                        old = candidates.get(key)
                        node = (new_snake, new_food, new_gain, new_risk, score)
                        if old is None or score > old[-1]:
                            candidates[key] = node
                        generated += 1
                        if generated & 15 == 0 and _clock() >= deadline:
                            raise _TimeUp
                survivors = sorted(
                    candidates.values(), key=lambda node: node[-1],
                    reverse=True
                )[:width]
                next_beams.append(survivors)
                if survivors:
                    next_quality[index] = survivors[0][-1]
                else:
                    next_dead[index] = depth
            beams = next_beams
            quality = next_quality
            dead = next_dead
        except _TimeUp:
            break
        if not any(beams):
            break
    return [
        (-9000.0 + 170.0 * depth) if depth else 0.40 * value
        for depth, value in zip(dead, quality)
    ]


class _Tactics:
    def __init__(self, game, selected):
        self.g = game
        self.b = game.b
        self.snakes = (game.me,) + tuple(
            game.enemies[i].snake for i in selected
        )
        outside = [enemy for i, enemy in enumerate(game.enemies)
                   if i not in selected]
        self.outside_count = len(outside)
        self.outside = _schedule(
            game.b, [e.snake for e in outside], game.horizon,
            [e.delay for e in outside]
        )
        self.nodes = 0

    def tick(self):
        self.nodes += 1
        if self.nodes & 15 == 0:
            self.g.check()

    def blocked(self, snakes, t):
        result = self.outside[t]
        for snake in snakes:
            if snake is not None:
                result |= _trim(snake, self.b)
        return result

    def moves(self, snake, blocked):
        if snake is None:
            return (-1,)
        options = tuple(
            q for q, _ in self.b.neighbors[snake[0][0]]
            if not (blocked & self.b.bits[q])
        )
        return options or (-1,)

    def combinations(self, snakes, food, blocked):
        board = self.b
        result = [((), 1.0)]
        my_options = self.moves(snakes[0], blocked)
        my_length = len(snakes[0][0])
        food_points = self.g.foods(food)
        for snake in snakes[1:]:
            options = self.moves(snake, blocked)
            weights = []
            for q in options:
                if q < 0 or snake is None:
                    weights.append(1.0)
                    continue
                bit = board.bits[q]
                degree = (board.adjacent[q] & ~blocked).bit_count()
                distance = _nearest(board, q, food_points)
                weight = (1.0 + degree * degree) / (1.0 + 0.20 * distance)
                if food & bit:
                    weight *= 2.5 + max(0, 55 - snake[1]) / 20.0
                elif snake[1] <= 1:
                    weight *= 0.03
                if my_length >= len(snake[0]) and q in my_options:
                    weight *= 0.18
                weights.append(max(0.025, weight))
            total = sum(weights)
            weighted = tuple((q, w / total)
                             for q, w in zip(options, weights))
            result = [
                (prefix + (q,), probability * weight)
                for prefix, probability in result
                for q, weight in weighted
            ]
        return result

    def transition(self, snakes, food, destinations, t):
        board = self.b
        count = len(snakes)
        advanced = [None] * count
        lengths = [0] * count
        alive = [False] * count
        remaining_food = food
        for i, (snake, q) in enumerate(zip(snakes, destinations)):
            if snake is None:
                continue
            lengths[i] = len(snake[0])
            if q < 0:
                continue
            new_snake = _advance(snake, q, food, board)
            advanced[i] = new_snake
            lengths[i] = len(new_snake[0])
            alive[i] = new_snake[1] > 0
            remaining_food &= ~board.bits[q]

        # All heads take part in the simultaneous collision resolution.
        for i in range(count):
            if snakes[i] is None or destinations[i] < 0:
                continue
            for j in range(i + 1, count):
                if snakes[j] is None or destinations[j] < 0:
                    continue
                if destinations[i] == destinations[j]:
                    if lengths[i] <= lengths[j]:
                        alive[i] = False
                    if lengths[j] <= lengths[i]:
                        alive[j] = False
        result = tuple(
            advanced[i] if alive[i] else None for i in range(count)
        )
        terminal = None
        if not alive[0]:
            if self.outside_count == 0:
                comparison = 0
                for i in range(1, count):
                    if snakes[i] is None:
                        comparison += 1
                    elif alive[i]:
                        comparison -= 1
                    else:
                        comparison += ((lengths[0] > lengths[i]) -
                                       (lengths[0] < lengths[i]))
                terminal = 9000.0 * comparison / max(1, count - 1)
                if terminal < 0:
                    terminal += min(100, 3 * t)
            else:
                simultaneous_deaths = sum(
                    snakes[i] is not None and not alive[i]
                    for i in range(1, count)
                )
                terminal = -9000.0 + 20.0 * t + 80.0 * simultaneous_deaths
        elif self.outside_count == 0 and not any(alive[1:]):
            terminal = 9000.0 - min(100, 3 * t)
        return result, remaining_food, terminal

    def finish(self, snakes):
        length = len(snakes[0][0])
        comparison = 0
        for snake in snakes[1:]:
            if snake is None:
                comparison += 1
            else:
                other = len(snake[0])
                comparison += (length > other) - (length < other)
        return 9000.0 * comparison / max(1, len(snakes) - 1)

    def leaf(self, snakes, food, ply):
        if ply >= self.g.remaining and self.outside_count == 0:
            return self.finish(snakes)
        board = self.b
        own = snakes[0]
        body, health, _ = own
        length = len(body)
        head = body[0]
        blocked = self.blocked(snakes, ply + 1)
        options = [
            q for q, _ in board.neighbors[head]
            if not (blocked & board.bits[q]) and
            (health > 1 or food & board.bits[q])
        ]
        if not options:
            return -8500.0 + 3.0 * ply
        danger = 0
        for snake in snakes[1:]:
            if snake is not None and len(snake[0]) >= length:
                for q in self.moves(snake, blocked):
                    if q >= 0:
                        danger |= board.bits[q]
        safe = sum(not (danger & board.bits[q]) for q in options)
        cap = min(96, max(20, length + 8))
        area = board.room(board.bits[head], blocked, cap).bit_count()
        deficit = max(0, min(cap, length + 3) - area)
        distance = _nearest(board, head, self.g.foods(food))
        value = (
            16.0 * (length - self.g.length) +
            0.04 * health + 5.0 * safe + 0.8 * len(options) +
            0.25 * min(area, cap) - 3.0 * deficit -
            (0.8 + 0.07 * max(0, 45 - health)) * distance
        )
        if not safe:
            value -= 90.0
        for snake in snakes[1:]:
            if snake is None:
                value += 65.0
                continue
            d = _distance(board, head, snake[0][0])
            if d <= 4:
                if len(snake[0]) >= length:
                    value -= 4.0 * (5 - d)
                else:
                    value += 1.5 * (5 - d)
        value -= 0.20 * (board.edge[head] == 0)
        value -= 0.01 * board.center[head]
        if food and distance > health:
            value -= 25.0 + 2.0 * (distance - health)
        return value

    def action(self, snakes, food, q, depth, ply, combinations,
               alpha=-1.0e100):
        worst = 1.0e100
        total = 0.0
        probability_seen = 0.0
        for destinations, probability in combinations:
            self.tick()
            new_snakes, new_food, terminal = self.transition(
                snakes, food, (q,) + destinations, ply + 1
            )
            if terminal is None:
                value = self.node(new_snakes, new_food, depth - 1, ply + 1)
            else:
                value = terminal
            worst = min(worst, value)
            total += probability * value
            probability_seen += probability
            upper = (0.75 * worst + 0.25 * (
                total + max(0.0, 1.0 - probability_seen) * 9000.0
            ))
            if upper <= alpha:
                return upper
        return 0.75 * worst + 0.25 * total

    def node(self, snakes, food, depth, ply):
        self.tick()
        if depth <= 0 or ply >= self.g.remaining:
            return self.leaf(snakes, food, ply)
        blocked = self.blocked(snakes, ply + 1)
        options = self.moves(snakes[0], blocked)
        combinations = self.combinations(snakes, food, blocked)
        best = -1.0e100
        for q in options:
            value = self.action(
                snakes, food, q, depth, ply, combinations, best
            )
            if value > best:
                best = value
            if best >= 9000.0:
                break
        return best

    def root_values(self, roots, depth):
        blocked = self.blocked(self.snakes, 1)
        combinations = self.combinations(self.snakes, self.g.food, blocked)
        values = []
        for root in roots:
            self.g.check()
            values.append(self.action(
                self.snakes, self.g.food, root["q"],
                depth, 0, combinations
            ))
        return values


def _choose(roots, beam_values, tactical_values=None, full_endgame=False):
    best_index = 0
    best_value = -1.0e100
    for i, root in enumerate(roots):
        positional = root["base"] + beam_values[i]
        if tactical_values is None:
            value = positional
        else:
            tactical = tactical_values[i]
            if full_endgame:
                value = (tactical + 0.001 * root["base"] +
                         0.0001 * beam_values[i])
            elif tactical >= 8000.0:
                value = 100000.0 + tactical + 0.01 * positional
            else:
                value = positional + 0.65 * tactical
        if value > best_value:
            best_index, best_value = i, value
    return best_index


def _run(state, started):
    global _backup, _target
    game = _Game(state, started)
    board = game.b
    neck = game.me[0][1] if len(game.me[0]) > 1 else -1
    physical = [
        (q, direction) for q, direction in board.neighbors[game.head]
        if q != neck
    ]
    legal = [
        (q, direction) for q, direction in physical
        if not (game.initial_block & board.bits[q]) and
        (game.health > 1 or game.food & board.bits[q])
    ]
    if not legal:
        if physical:
            q, direction = max(
                physical,
                key=lambda item: (
                    bool(game.food & board.bits[item[0]]),
                    not bool(game.initial_block & board.bits[item[0]]),
                    _NAMES[item[1]] == game.current_direction
                )
            )
            return _NAMES[direction]
        return game.current_direction

    def emergency_value(move):
        q, direction = move
        danger = sum(
            len(snake[0]) >= game.length and q in options
            for snake, options in zip(game.snakes[1:], game.options[1:])
        )
        degree = (board.adjacent[q] & ~game.initial_block).bit_count()
        return (6.0 * bool(game.food & board.bits[q]) + degree -
                100.0 * danger +
                0.1 * (_NAMES[direction] == game.current_direction))

    _, direction = max(legal, key=emergency_value)
    _backup = _NAMES[direction]
    if len(legal) == 1:
        return _backup

    game.prepare()
    roots = []
    for q, direction in legal:
        root = {
            "q": q,
            "direction": direction,
            "snake": _advance(game.me, q, game.food, board)
        }
        _root_score(game, root)
        roots.append(root)
    zero = [0.0] * len(roots)
    selected_root = _choose(roots, zero)
    _backup = _NAMES[roots[selected_root]["direction"]]

    close = []
    force_endgame = len(game.snakes) == 2 and game.remaining <= 5
    for i, enemy in enumerate(game.enemies):
        distance = _distance(board, game.head, enemy.head)
        if distance <= 8 or force_endgame:
            priority = distance - (1 if enemy.length >= game.length else 0)
            close.append((priority, distance, i))
    close.sort()
    selected = [entry[2] for entry in close[:2]]
    width = 8 if selected else 12
    if game.length > 80:
        width = min(width, 6)
    beam_deadline = (
        min(started + 0.021, game.deadline - 0.009)
        if selected else game.deadline - 0.0015
    )
    beam_values = _beam(game, roots, beam_deadline, width)
    selected_root = _choose(roots, beam_values)
    _backup = _NAMES[roots[selected_root]["direction"]]

    tactical_values = None
    full_endgame = False
    if selected and _clock() < game.deadline:
        search = _Tactics(game, selected)
        max_depth = min(game.remaining, 5 if len(selected) == 1 else 3)
        try:
            for depth in range(1, max_depth + 1):
                game.check()
                values = search.root_values(roots, depth)
                tactical_values = values
                full_endgame = (
                    depth >= game.remaining and search.outside_count == 0
                )
                selected_root = _choose(
                    roots, beam_values, tactical_values, full_endgame
                )
                _backup = _NAMES[roots[selected_root]["direction"]]
                if full_endgame:
                    break
        except _TimeUp:
            pass
    selected_root = _choose(
        roots, beam_values, tactical_values, full_endgame
    )
    _target = roots[selected_root]["target"]
    return _NAMES[roots[selected_root]["direction"]]


def decide(state):
    global _backup, _last_direction
    started = _clock()
    _backup = _last_direction
    try:
        answer = _run(state, started)
    except Exception:
        answer = _backup
    if answer not in _NAMES:
        answer = "up"
    _last_direction = answer
    return answer
