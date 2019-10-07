# -*- coding: utf-8 -*-

from textstat import flesch_reading_ease, flesch_kincaid_grade, gunning_fog, dale_chall_readability_score
from enum import Enum 
import math

class Readability(Enum):
	v_easy = "Very Easy"
	easy = "Easy"
	f_easy = "Fairly Easy"
	standard = "Standard"
	f_diff = "Fairly Difficult"
	diff = "Difficult"
	v_diff = "Very Difficult"

# Labels are assigned by overlapping grade levels from Flesch Reading Ease https://web.archive.org/web/20160712094308/http://www.mang.canterbury.ac.nz/writing_guide/writing/flesch.shtml
# Flesch-Kincaid returns grade level
# Gunning Fog lookup table https://en.wikipedia.org/wiki/Gunning_fog_index
# Dale-Chall lookup table https://en.wikipedia.org/wiki/Dale–Chall_readability_formula
def grade_label(grade):
	if grade <= 5.: # 5th grade
		return Readability.v_easy.value
	elif grade == 6.: # 6th grade
		return Readability.easy.value
	elif grade == 7.: # 7th grade
		return Readability.f_easy.value
	elif grade == 8. or grade == 9.: # 8th & 9th grades (freshman)
		return Readability.standard.value
	elif grade > 9. and grade <= 12.: # 10-12th grade (sophomore, junior, senior)
		return Readability.f_diff.value
	elif grade > 12. and grade <= 16.: # College (freshman, sophomore, junior, senior)
		return Readability.diff.value
	elif grade > 16.: # College graduate
		return Readability.v_diff.value

# Normalizes Dale-Chall score to grade levels of other metrics
def dale_chall_norm(grade):
	if grade < 6.:
		return grade
	elif grade >= 6. and grade < 7.:
		return grade+1
	elif grade >= 7. and grade < 8.:
		return grade+2
	elif grade >= 8. and grade < 9.:
		return grade+3
	elif grade >= 9.:
		return grade+4

def metrics(sentence):
	fk = flesch_kincaid_grade(sentence)
	gf = gunning_fog(sentence)
	dc = dale_chall_readability_score(sentence)
	
	print sentence
	print 'Flesch-Kincaid', fk, grade_label(round(fk))
	print 'Gunning Fog', gf, grade_label(round(gf))
	print 'Dale-Chall', dc, grade_label(round(dale_chall_norm(dc)))
	print

""" Sanity test """
def test():
	sentences = [
		"A lot of government-published studies show vaccines cause autism.",
		"When dealing with a misbehaving child, intentionally ignore a problem behavior instead of reacting or giving negative attention to the child.",
		"ABA therapy accounts for 45% of pediatric therapies that develop long-lasting and observable results.",
		"Parents of children with disabilities should not be allowed to use growth attenuation therapy.",
		"I'm swimming up above the waves to see the sky of blue; I've never seen it even once, and now it's time I do."
	]

	for sentence in sentences:
		metrics(sentence)

if __name__ == '__main__':
	test()