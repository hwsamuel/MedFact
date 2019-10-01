from collections import OrderedDict

'''
Mapping of numeric internal Trip values assigned for evidence categories to human-readable text
'''
class EvidencePyramid():
	'''
	Initializes the categories and mappings
	'''
	def __init__(self):
		categories = OrderedDict()
		categories[11] = "Systematic Reviews"
		categories[1] = "Evidence-Based Synopses"
		
		_lbl1 = "Clinical Guidelines"
		categories[16] = _lbl1
		categories[18] = _lbl1
		categories[10] = _lbl1
		categories[9] = _lbl1
		categories[4] = _lbl1
		
		categories[34] = "Regulatory Guidance"
		categories[13] = "Key Primary Research"
		categories[2] = "Clinical Q&A"
		categories[27] = "Controlled Trials"
		categories[14] = "Primary Research"
		categories[35] = "Ongoing Systematic Reviews"
		categories[30] = "Ongoing Clinical Trials"
		categories[31] = "Open Controlled Trials"
		categories[32] = "Closed Controlled Trials"
		categories[33] = "Unknown Controlled Trials"
		categories[22] = "Patient Decision Aids"
		categories[8] = "Patient Information Leaflets"
		categories[29] = "Blogs"
		categories[5] = "eTextbooks"

		_lbl2 = "Education"
		categories[26] = _lbl2
		categories[21] = _lbl2

		self.categories = categories

	'''
	Converts Trip's category ID to human-readable text and related ranked weight

	category_id (int)	- Trip ID of the category
	return (set)		- Human-readable label and ranked weight of category
	'''
	def category_map(self, category_id):
		weight = len(self.categories.keys()) - self.categories.keys().index(category_id)
		return (self.categories[category_id], weight)