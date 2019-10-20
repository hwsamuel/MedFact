import sqlite3, smtplib
import medfact, scraper

def main():
	db = sqlite3.connect('batch.sqlite')
	cursor = db.cursor()
	cursor.execute("SELECT * FROM jobs WHERE status = 0")
	results = cursor.fetchone()
	if results == None: return

	id = results[0]
	mode = results[1]
	content = results[2]
	email = results[3]

	if mode == medfact.BatchMode.Text.value:
		v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label = medfact.score_sentences(content)
		msg = 'Veracity Score\t%s\nConfidence Score\t%s\nTriage Label\t%s\nFlesch-Kincaid Score\t%s\nGunning Fog Score\t%s\nDale-Chall Score\t%s\nFlesch-Kincaid Label\t%s\nGunning Fog Label\t%s\nDale-Chall Label\t%s\n\nOriginal Text\n%s' % (v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label, content)
	elif mode == medfact.BatchMode.URL.value:
		urls = content.split('\n')
		msg = ''
		for url in urls:
			text = scraper.get_body(url)
			v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label = medfact.score_sentences(text)
			msg += 'URL\t%s\nVeracity Score\t%s\nConfidence Score\t%s\nTriage Label\t%s\nFlesch-Kincaid Score\t%s\nGunning Fog Score\t%s\nDale-Chall Score\t%s\nFlesch-Kincaid Label\t%s\nGunning Fog Label\t%s\nDale-Chall Label\t%s\n\n' % (url, v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label)

	send_mail(msg, "MedFact Analysis Results", "hwsamuel@ualberta.ca")
	
	cursor.execute("UPDATE jobs SET status = 1 WHERE id = ?", (id,))
	db.commit()
	db.close()

def send_mail(text, subject, recipient):
	sender = "addr@gmail.com"
	password = "app-password" # https://support.google.com/accounts/answer/185833?hl=en
	server = "smtp.gmail.com"
	port = 465
	
	smtp_server = smtplib.SMTP_SSL(server, port)
	smtp_server.login(sender, password)
	message = "Subject: {}\n\n{}".format(subject, text)
	smtp_server.sendmail(sender, [recipient], message)
	smtp_server.close()

if __name__ == '__main__':
	main()