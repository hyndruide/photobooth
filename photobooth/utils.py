import pygame


def paragraph(text_string, font, color, align):
	text_blit_array = []
	text_array = text_string.splitlines()
	width_total = 0
	height_total = 0
	
	for text in text_array:
		text_line = font.render(text, 1, color)
		w,h = text_line.get_size()
		if width_total < w:
			width_total =  w 
		height_total = height_total + h
		text_blit_array.append(text_line)
	text_Surface = pygame.Surface((width_total,height_total),flags=pygame.SRCALPHA)
	pos=(0,0)

	if align == "left":
		for text_blit in text_blit_array:
			text_Surface.blit(text_blit,(0,pos[1]))
			posw,posh =  text_blit.get_size()
			pos = posw , pos[1]+posh
	if align == "center":
		for text_blit in text_blit_array:
			text_Surface.blit(text_blit,((text_Surface.get_width() /2) - (text_blit.get_width()/2) ,pos[1]))
			posw,posh =  text_blit.get_size()
			pos = posw , pos[1]+posh
	if align == "right":
		for text_blit in text_blit_array:
			text_Surface.blit(text_blit,((text_Surface.get_width() ) - (text_blit.get_width()) ,pos[1]))
			posw,posh =  text_blit.get_size()
			pos = posw , pos[1]+posh
	return text_Surface

def position(surf_base,surf_to_blit,v_align = "center",h_align = "center"):
	if v_align == "left":
		v_pos =  0
	if v_align == "center":
		v_pos =  int((surf_base.get_width() / 2) - (surf_to_blit.get_width() / 2))
	if v_align == "right":
		v_pos =  int(surf_base.get_width() - surf_to_blit.get_width())


	if type(h_align) == int:
		h_pos = h_align
	else:
		if h_align == "top":
			h_pos =  0
		if h_align == "center":
			h_pos =  int((surf_base.get_height() / 2) - (surf_to_blit.get_height() / 2))
		if h_align == "center_top":
			h_pos =  int(30)
		if h_align == "bottom":
			h_pos = int(surf_base.get_height() - surf_to_blit.get_height()-10)
	return (v_pos,h_pos)