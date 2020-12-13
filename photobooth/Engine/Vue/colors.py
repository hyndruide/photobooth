COLORS = dict(
    BLACK=(0, 0, 0),
    ORANGE=(242, 101, 34),
    WHITE=(255, 255, 255),
    RED=(255, 0, 0),
)


def get(name):
    return COLORS.get(name, name)