import re, time

start_time = time.time()

head_before_title = "<!doctype html>\n<html>\n<head>\n\t<title>"
head_after_title=" Dynasty</title>\n<link rel='stylesheet' href='style.css'>\n</head>\n<body>"
end_body = "</body></html>"

html = ""

dynasties = {}
titles = {}

title_holders = {}

chars_done = []
children = {}



ho = ""

class Character(object):

	fat_patt = re.compile("(father|fat)=(\d+)")
	mot_patt = re.compile("(mother|mot)=(\d+)")
	gender_string = "female=yes"
	bn_patt = re.compile("(birth_name|bn)=\"(.*)\"")
	dyn_patt = re.compile("dynasty=(\d+)")
	holding_pattern_1 = re.compile('primary=\s*{\s*title="(.*?)"')
	holding_pattern_2 = re.compile('old_holding="(.*?)"')
	#def readable_title():
	
	
	def __init__(self, character, block):
		self.id = character
		self.block = block
		self.gender = "female" if self.gender_string in block else "male"
		self.name = "Unknown"
		self.father = -1
		self.mother = -1
		self.dynasty = dynasties[-1]
		self.holding = ""
		self.position = ""
		name_match = self.bn_patt.search(block)
		if (name_match != None):
			self.name = name_match.group(2)
		father_match = self.fat_patt.search(block)
		if (father_match != None):
			self.father = father_match.group(2)
			children[self.father] = children.get(self.father, [])
			children[self.father].append(character)
		mother_match = self.mot_patt.search(block)
		if (mother_match != None):
			self.mother = mother_match.group(2)
			children[self.mother] = children.get(self.mother, [])
			children[self.mother].append(character)
		dynasty_match = self.dyn_patt.search(block)
		if (dynasty_match != None):
			dynasty_id = dynasty_match.group(1)
			self.dynasty = dynasties[dynasty_id]
		holding_match = self.holding_pattern_1.search(block)
		if (holding_match != None):
			self.holding = holding_match.group(1)
		else:
			holding_match = self.holding_pattern_2.search(block)
			if (holding_match != None):
				self.holding = holding_match.group(1)
			else:
				if self.id in title_holders:
					self.holding = title_holders[self.id]
		if (self.holding != ""):
			if any(x in self.holding for x in ['band', 'host', 'revolt']) or "_dyn_" in self.holding:
				#print self.holding, " # ",
				self.position = titles[self.holding].title
				self.holding = titles[self.holding].name
				#print self.holding
			type = self.holding[0]
			self.holding = self.holding[2:].capitalize()
			if "_" in self.holding:
				self.holding = " ".join([h.capitalize() for h in self.holding.split("_")])
			if (type == "e"):
				self.holding = ("Empress of " if self.gender == "female" else "Emperor of ") + self.holding
				self.position = "emperor"
			elif (type == "l"):
				print "GGG " + self.position + " HHH " + self.holding
				self.holding = self.position.capitalize() + " of " + self.holding
			elif (type == "k"):
				self.holding = ("Queen of " if self.gender == "female" else "King of ") + self.holding
				self.position = "king"
			elif (type == "d"):
				self.holding = ("Duchess of " if self.gender == "female" else "Duke of ") + self.holding
				self.position = "duke"
			elif (type == "c"):
				self.holding = ("Countess of " if self.gender == "female" else "Count of ") + self.holding
				self.position = "count"
			elif (type == "b"):
				self.holding = ("Baroness of " if self.gender == "female" else "Baron of ") + self.holding
				self.position = "baron"
				
		
		
class Dynasty(object):
	name_patt = re.compile("name=\"(.*)\"")
	def __init__(self, dynasty, block):
		self.id = dynasty
		self.name = "NoDYN"
		name_match = self.name_patt.search(block)
		if (name_match != None):
			self.name = name_match.group(1)
		
class Title(object):
	dynamic_holding_patt = re.compile("\n\t\t\tname=\"(.*?)\"")
	holder_patt = re.compile("holder=(\d+)")
	title_patt = re.compile('title="(.*?)"')	
	def __init__(self, title, block):
		global ho
		ho += title + "\n"
		self.id = title
		self.name = title
		self.type = title[0]
		self.title = "Leader"
		if 'landless=yes' in block:
			title_match = self.title_patt.search(block)
			self.type = "l"
			if (title_match != None):
				self.title = title_match.group(1)
		if "_dyn_" in title:
			dynamic_holding_match = self.dynamic_holding_patt.search(block)
			if (dynamic_holding_match != None):
				self.name = (self.type + "_" + dynamic_holding_match.group(1)).replace(" ", "_").lower()
		holder_match = self.holder_patt.search(block)
		if (holder_match != None):
			holder = holder_match.group(1)
			current_held = title_holders.get(holder, " ")[0]
			if (self.type == "b" and (current_held not in "ekdc")):
				title_holders[holder] = self.name
			elif (self.type == "c" and (current_held not in "ekd")):
				title_holders[holder] = self.name
			elif (self.type == "d" and (current_held not in "ek")):
				title_holders[holder] = self.name
			elif (self.type == "k" and (current_held not in "e")):
				title_holders[holder] = self.name
			elif (self.type == "e"):
				title_holders[holder] = self.name
			elif (self.type == "l"):
				title_holders[holder] = self.name
		titles[self.name] = self
		

def dict_by_list(char):
	print "Beginning list method"
	start_time = time.time()
	char_patt = re.compile('(\d+)=')
	it = char_patt.finditer(char)
	characters = {}
	l = list(it)
	length = len(l)
	print length
	for i in xrange(length):
		match = l[i]
		character = match.group(1)
		start = match.start()
		if (i != (length - 1)):
			characters[character] = Character(character, char[start:l[i+1].start()])
		else:
			characters[character] = Character(character, char[start:])
	print len(characters)
	end_time = time.time()
	print("Elapsed time was %g seconds" % (end_time - start_time))
	return characters


def dict_by_iter(char):
	print "Beginning iter method"
	char_patt = re.compile('(\d+)=')
	it = char_patt.finditer(char)
	characters = {}
	cnt = 0
	start_time = time.time()
	match = next(it, None)
	start = match.start()
	character = match.group(1)
	while (match != None):
		match = next(it, None)
		if (match != None):
			characters[character] = Character(character, char[start:match.start()])
		else:
			characters[character] = Character(character, char[start:])
			break
		start = match.start()
		character = match.group(1)
		cnt += 1
	end_time = time.time()
	print("Elapsed time was %g seconds" % (end_time - start_time))
	return characters
	
def get_characters(char):
	return dict_by_list(char)
	
	
def dict_dyn(dyn):
	print "Beginning list method"
	start_time = time.time()
	dyn_patt = re.compile('(\d+)=')
	it = dyn_patt.finditer(dyn)
	#dynasties = {}
	l = list(it)
	length = len(l)
	print length
	for i in xrange(length):
		match = l[i]
		dynasty = match.group(1)
		start = match.start()
		if (i != (length - 1)):
			dynasties[dynasty] = Dynasty(dynasty, dyn[start:l[i+1].start()])
		else:
			dynasties[dynasty] = Dynasty(dynasty, dyn[start:])
	dynasties[-1] = Dynasty(-1, "name=\"(Lowborn)\"")
	print len(dynasties)
	end_time = time.time()
	print("Elapsed time was %g seconds" % (end_time - start_time))
	return dynasties
	
	
	
def get_dynasties(dyn):
	return dict_dyn(dyn)

def update_dynasties(dyn):
	return dict_dyn(dyn)

def dict_titles(raw_titles):
	print "Beginning list method"
	start_time = time.time()
	title_patt = re.compile('([ekdcb]_[\d\w_]+)=\s+{')
	it = title_patt.finditer(raw_titles)
	l = list(it)
	length = len(l)
	print length
	for i in xrange(length):
		match = l[i]
		title = match.group(1)
		start = match.start()
		if (i != (length - 1)):
			titles[title] = Title(title, raw_titles[start:l[i+1].start()])
		else:
			titles[title] = Title(title, raw_titles[start:])
	titles[-1] = Title("notitle", "")
	print len(titles)
	end_time = time.time()
	print("Elapsed time was %g seconds" % (end_time - start_time))
	return titles
	
def get_titles(raw_titles):
	return dict_titles(raw_titles)

def get_block(start, char):
	lines = char.split('\n')
	count = 0
	block = ""
	for line in lines:
		for char in line:
			block += char
			if (char == '{'):
				count += 1
			elif (char == '}'):
				count -= 1
				if count == 0:
					return block
		block += "\n"


def get_ancestor(player, char, characters):
	block = characters[player].block
	bn = characters[player].name
	print bn, "->",
	father_reg = characters[player].father
	if (father_reg == -1):
		return player
	father = characters[player].father
	return get_ancestor(father, char, characters)
	
def get_children(player, characters, dynasties, titles, count = 0):
	global html
	current_parent = characters[player]
	if (count == 0):
		title = current_parent.name
		html += head_before_title + title + head_after_title
		html += "<ol><li>" + "<b>" + title + " "  + current_parent.dynasty.name + ", " + current_parent.holding + "</b>"
	chars_done.append(player)
	total_kids = sorted(children.get(player, []))
	boys = []
	girls = []
	for child in total_kids:
		if (characters[child].gender == "female"):
			girls.append(child)
		else:
			boys.append(child)
	kids = boys + girls
	html += "<ol>\n"
	previous_parent_id = -2
	for child in kids:
		character = characters[child]
		mother = characters[character.mother]
		father = characters[character.father]
		dynasty = character.dynasty
		other_parent = father if (current_parent.gender == "female") else mother
		if (other_parent.id != previous_parent_id):
			html += "with " + other_parent.name + " " + other_parent.dynasty.name + ", " + other_parent.holding
			previous_parent_id = other_parent.id
		#for i in xrange(count):
		#	print " ",
		#	html += "&nbsp;"
		#print character.id, character.gender, 
		if (character.position != ""):
			html += '<li class="' + character.position + '">'
		else:
			html += '<li>'
		html += '' + "<b>" + character.name + " " + character.dynasty.name + ", " + character.holding + "</b>"
		#print character.name,
		#print dynasty.name,
		#print character.mother
		#print " Mother: ", mother.name, #mother.dynasty,
		#print dynasties[mother.dynasty].name
		#print character.father, father.name, dynasties[father.dynasty].name,
		#print dynasty.id,
		if character.id not in chars_done:
			get_children(character.id, characters, dynasties, titles, count + 1)
		html += "</li>\n"
	html += "</ol>\n"


s = open("save.ck2", "r").read();

player = s.find("player=");

dyn_start = s.find("dynasties=\n")
char_start = s.find("character=\n")
delayed_start = s.find("delayed_event=")
relat_start = s.find("\trelation=\n")
titles_start = s.find("\n\ttitle=")
nomad_start = s.find("\n\tnomad=")

print dyn_start, char_start, delayed_start

dyn = s[dyn_start:char_start]
#d = open("dynasties.cksour", "w")
#d.write(dynasties)
#d.close()

get_dynasties(dyn)

dyn = open("00_dynasties.txt", "r").read()
update_dynasties(dyn)



raw_titles = s[titles_start:nomad_start]
get_titles(raw_titles)

open("holdings.txt", "w").write(ho)

char = s[char_start:delayed_start]
#d = open("characters.cksour", "w")
#d.write(characters)
#d.close()

player = "606574"

characters = get_characters(char)
characters[-1] = Character(-1, "UNKNOWN2")



anc = get_ancestor(player, char, characters)
print "ROOT: " + anc

kdis = get_children(anc, characters, dynasties, titles)
html +=  "</li></ol>"
end_time = time.time()
print("Elapsed time was %g seconds" % (end_time - start_time))

#print html
treepage = open("tree.html", "w")
treepage.write(html)

print len(chars_done)
print "END"