from textwrap import TextWrapper
from .utils import is_emoji


class CustomTextWrapper(TextWrapper):
    """
    Модификация TextWrapper.
    Нужен из-за появления эмодзи
    """

    def __init__(self, font, width=70, **kwargs):
        super().__init__(width, **kwargs)
        self.font = font

    def get_chunk_len(self, chunk):
        """
        Подсчёт длины куска. Создан вследствие
        разной длины эмодзи и шрифта.
        """
        counter = 0
        for c in chunk:
            if not is_emoji(c):
                counter += self.font.getsize(c)[0]
            else:
                counter += self.font.size
        return counter

    def _wrap_chunks(self, chunks):
        """
        Модификация TextWrapper._wrap_chunks.
        Заменяет логику подсчёта длины куска с len на get_chunk_len.
        """
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if self.max_lines is not None:
            if self.max_lines > 1:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            if len(indent) + len(self.placeholder.lstrip()) > self.width:
                raise ValueError("placeholder too large for max width")

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = self.get_chunk_len(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and self.get_chunk_len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
                cur_len = sum(map(self.get_chunk_len, cur_line))

            # If the last chunk on this line is all whitespace, drop it.
            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                cur_len -= self.get_chunk_len(cur_line[-1])
                del cur_line[-1]

            if cur_line:
                if (self.max_lines is None or
                        len(lines) + 1 < self.max_lines or
                        (not chunks or
                         self.drop_whitespace and
                         len(chunks) == 1 and
                         not chunks[0].strip()) and cur_len <= width):
                    # Convert current line back to a string and store it in
                    # list of all lines (return value).
                    lines.append(indent + ''.join(cur_line))
                else:
                    while cur_line:
                        if (cur_line[-1].strip() and
                                cur_len + len(self.placeholder) <= width):
                            cur_line.append(self.placeholder)
                            lines.append(indent + ''.join(cur_line))
                            break
                        cur_len -= self.get_chunk_len(cur_line[-1])
                        del cur_line[-1]
                    else:
                        if lines:
                            prev_line = lines[-1].rstrip()
                            if (len(prev_line) + len(self.placeholder) <=
                                    self.width):
                                lines[-1] = prev_line + self.placeholder
                                break
                        lines.append(indent + self.placeholder.lstrip())
                    break

        return lines


def wrap(text, font, width=70, **kwargs):
    w = CustomTextWrapper(width=width, font=font, **kwargs)
    return w.wrap(text)
