# ! -*- coding: utf-8 -*-


class TicTacField(object):

    def __init__(self, size, min_length, allow_horizontal, allow_vertical, allow_diagonal, field=None):
        self._size = size
        self._min_length = min_length
        self._allow_horizontal = allow_horizontal
        self._allow_vertical = allow_vertical
        self._allow_diagonal = allow_diagonal
        if field is not None:
            self._field = field
        else:
            self._field = [[None] * self._size for x in range(self._size)]

    def get_cell(self, x, y):
        return self._field[x][y]

    def set_cell(self, x, y, val):
        self._field[x][y] = val

    def check_lines(self, x, y):
        for line in self.line_generator(x, y):
            if len(set(map(lambda x: x[2], line))) == 1:
                return line
        return None

    def get_line(self, x, y, walker):
        line = []
        for i in range(self._min_length):
            line.append((x, y, self.get_cell(x, y)))
            x, y = walker(x, y)
        return line

    def line_generator(self, x, y):
        length = self._min_length - 1
        x_left = max(x - length, 0)
        y_bottom = max(y - length, 0)
        y_top = min(y + length, self._size - 1)

        if self._allow_horizontal:
            x_start = x_left
            while x_start + length < self._size and x_start <= x:
                yield self.get_line(x_start, y, lambda x, y: (x + 1, y))
                x_start += 1
        if self._allow_vertical:
            y_start = y_bottom
            while y_start + length < self._size and y_start <= y:
                yield self.get_line(x, y_start, lambda x, y: (x, y + 1))
                y_start += 1
        if self._allow_diagonal:
            y_start = y - min(x - x_left, y - y_bottom)
            x_start = x - min(x - x_left, y - y_bottom)
            while y_start + length < self._size and x_start + length < self._size and x_start <= x and y_start <= y:
                yield self.get_line(x_start, y_start, lambda x, y: (x + 1, y + 1))
                x_start += 1
                y_start += 1
            y_start = y + min(x - x_left, y_top - y)
            x_start = x - min(x - x_left, y_top - y)
            while y_start - length >= 0 and x_start + length < self._size and x_start <= x and y_start >= y:
                yield self.get_line(x_start, y_start, lambda x, y: (x + 1, y - 1))
                x_start += 1
                y_start -= 1

    @classmethod
    def from_game(cls, game):
        return cls(
            size=game.size,
            min_length=game.min_length,
            allow_horizontal=game.allow_horizontal,
            allow_vertical=game.allow_vertical,
            allow_diagonal=game.allow_diagonal,
        )


class TicTacFieldSerializer(object):

    @classmethod
    def serialize(cls, obj):
        return {
            "size": obj._size,
            "min_length": obj._min_length,
            "allow_horizontal": obj._allow_horizontal,
            "allow_vertical": obj._allow_vertical,
            "allow_diagonal": obj._allow_diagonal,
            "field": obj._field,
        }

    @classmethod
    def restore(cls, data):
        return TicTacField(
            size=data['size'],
            min_length=data['min_length'],
            allow_horizontal=data['allow_horizontal'],
            allow_vertical=data['allow_vertical'],
            allow_diagonal=data['allow_diagonal'],
            field=data['field'],
        )
