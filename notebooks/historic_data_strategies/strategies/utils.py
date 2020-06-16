def lay_hedge_threshold(bp, c):
	return round((bp - 1) * (1 - c) + 1, 2)

def back_hedge_threshold(lp, c):
	return (c ** 2 - 2 * c + lp) / (1 - c) ** 2

def lay_hedge_stake(bp, bs, lp, c):
    return round((((bp - 1) * bs * (1 - c)) + bs) / (lp - c), 2)