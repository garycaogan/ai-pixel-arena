"""贪吃蛇大乱斗的规则引擎。纯函数、确定性：同一个种子加同一串走法，结果永远一样。

坐标 (x, y)：x 从左到右 0..W-1，y 从上到下 0..H-1。up = y-1。
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
LETTER = {"up": "U", "down": "D", "left": "L", "right": "R"}
FROM_LETTER = {v: k for k, v in LETTER.items()}

MAX_HEALTH = 100
START_LENGTH = 3


def board_size(n: int) -> int:
    return 15 if n == 2 else 21 if n <= 4 else 31


def max_turns(n: int) -> int:
    return 500 if n == 2 else 800


def food_target(n: int) -> int:
    return n + 1


@dataclass
class Snake:
    id: int
    body: list[tuple[int, int]]
    health: int = MAX_HEALTH
    alive: bool = True
    death_turn: int = 0
    death_cause: str = ""
    killer: int | None = None
    length_at_death: int = 0
    ate: int = 0
    kills: int = 0

    @property
    def head(self):
        return self.body[0]

    def direction(self) -> str | None:
        if len(self.body) < 2 or self.body[0] == self.body[1]:
            return None
        dx, dy = self.body[0][0] - self.body[1][0], self.body[0][1] - self.body[1][1]
        for name, d in DIRS.items():
            if d == (dx, dy):
                return name
        return None


@dataclass
class Game:
    n: int
    seed: int
    width: int = 0
    height: int = 0
    turn: int = 0
    snakes: list[Snake] = field(default_factory=list)
    food: list[tuple[int, int]] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
    events: list[dict] = field(default_factory=list)

    @classmethod
    def new(cls, n: int, seed: int) -> "Game":
        g = cls(n=n, seed=seed)
        g.width = g.height = board_size(n)
        g.rng = random.Random(seed * 7919 + n)
        spawns = g._spawn_points()
        for i in range(n):
            g.snakes.append(Snake(id=i, body=[spawns[i]] * START_LENGTH))
        for _ in range(food_target(n)):
            g._spawn_food()
        return g

    def _spawn_points(self):
        """出生点：两人局在对角，多人局沿一圈均匀排开。座位顺序就是 id 顺序。"""
        w = self.width
        if self.n == 2:
            return [(3, 3), (w - 4, w - 4)]
        import math
        c = (w - 1) / 2
        r = w * 0.36
        pts = []
        for i in range(self.n):
            a = -math.pi / 2 + 2 * math.pi * i / self.n
            pts.append((int(round(c + r * math.cos(a))), int(round(c + r * math.sin(a)))))
        return pts

    def occupied(self):
        occ = set()
        for s in self.snakes:
            if s.alive:
                occ.update(s.body)
        return occ

    def _spawn_food(self):
        occ = self.occupied() | set(self.food)
        free = [(x, y) for y in range(self.height) for x in range(self.width) if (x, y) not in occ]
        if free:
            self.food.append(free[self.rng.randrange(len(free))])

    def alive(self):
        return [s for s in self.snakes if s.alive]

    def over(self) -> bool:
        return len(self.alive()) <= 1 or self.turn >= max_turns(self.n)

    def state_for(self, sid: int) -> dict:
        return {
            "turn": self.turn + 1,
            "max_turns": max_turns(self.n),
            "width": self.width,
            "height": self.height,
            "num_snakes": self.n,
            "you": sid,
            "snakes": [{"id": s.id, "body": [list(p) for p in s.body], "health": s.health, "length": len(s.body)}
                       for s in self.snakes if s.alive],
            "food": [list(p) for p in self.food],
        }

    def step(self, moves: dict[int, str]) -> list[dict]:
        """moves: 每条活蛇这回合的方向（已经由裁判把无效答案换成直行）。返回本回合的事件。"""
        self.turn += 1
        ev: list[dict] = []
        alive = self.alive()
        # 1 移动：掉头无效，按原方向继续
        for s in alive:
            mv = moves.get(s.id)
            cur = s.direction()
            if mv not in DIRS:
                mv = cur or "up"
            if cur and DIRS[mv][0] == -DIRS[cur][0] and DIRS[mv][1] == -DIRS[cur][1]:
                mv = cur
            dx, dy = DIRS[mv]
            s.body.insert(0, (s.head[0] + dx, s.head[1] + dy))
            s.body.pop()
        # 2 饥饿
        for s in alive:
            s.health -= 1
        # 3 吃食物
        eaten = set()
        for s in alive:
            if s.head in self.food:
                eaten.add(s.head)
                s.health = MAX_HEALTH
                s.body.append(s.body[-1])
                s.ate += 1
                ev.append({"t": self.turn, "type": "eat", "id": s.id, "at": list(s.head)})
        if eaten:
            self.food = [f for f in self.food if f not in eaten]
        # 4 淘汰（同时判定）
        dead: dict[int, tuple[str, int | None]] = {}
        bodies = {}
        for s in alive:
            for p in s.body[1:]:
                bodies.setdefault(p, s.id)
        heads: dict[tuple[int, int], list[Snake]] = {}
        for s in alive:
            heads.setdefault(s.head, []).append(s)
        for s in alive:
            x, y = s.head
            if not (0 <= x < self.width and 0 <= y < self.height):
                dead[s.id] = ("wall", None)
            elif s.health <= 0:
                dead[s.id] = ("starve", None)
            elif s.head in bodies:
                owner = bodies[s.head]
                dead[s.id] = ("self" if owner == s.id else "body", None if owner == s.id else owner)
        for pos, group in heads.items():
            if len(group) < 2:
                continue
            longest = max(len(s.body) for s in group)
            winners = [s for s in group if len(s.body) == longest]
            for s in group:
                if len(winners) > 1 or s is not winners[0]:
                    other = winners[0].id if len(winners) == 1 else next(o.id for o in group if o is not s)
                    dead.setdefault(s.id, ("head", other))
        for sid, (cause, killer) in sorted(dead.items()):
            s = self.snakes[sid]
            s.alive = False
            s.death_turn = self.turn
            s.death_cause = cause
            s.killer = killer
            s.length_at_death = len(s.body)
            if killer is not None and killer != sid:
                self.snakes[killer].kills += 1
            ev.append({"t": self.turn, "type": "die", "id": sid, "cause": cause, "by": killer,
                       "at": list(s.head), "len": len(s.body)})
        # 5 补食物
        while len(self.food) < food_target(self.n):
            before = len(self.food)
            self._spawn_food()
            if len(self.food) == before:
                break
        self.events.extend(ev)
        return ev

    def placements(self) -> list[int]:
        """每条蛇的名次（1 最好，可并列）：活得久的靠前；同一回合死的、或都活到最后的，比长度。"""
        key = {}
        for s in self.snakes:
            if s.alive:
                key[s.id] = (10 ** 6, len(s.body))
            else:
                key[s.id] = (s.death_turn, s.length_at_death)
        return [1 + sum(key[o.id] > key[s.id] for o in self.snakes) for s in self.snakes]


def replay(n: int, seed: int, move_rows: list[str]) -> Game:
    """按记录的走法重放一局。move_rows[t] 是第 t+1 回合每条蛇的方向字母（死蛇是 '.'）。"""
    g = Game.new(n, seed)
    for row in move_rows:
        moves = {i: FROM_LETTER[c] for i, c in enumerate(row) if c in FROM_LETTER and g.snakes[i].alive}
        g.step(moves)
    return g
