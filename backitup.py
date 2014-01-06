import email, getpass, imaplib, os

def replace_all(text, l):
    for i in l:
        text = text.replace(i, "_")
    return text

user = raw_input("Enter your GMail username:")
pwd = getpass.getpass("Enter your password: ")

m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user,pwd)
m.select('"[Gmail]/All Mail"')

resp, items = m.search(None, "ALL")
items = items[0].split()

if os.name == 'posix':
    detach_dir = '/Users/'+os.getlogin()+'/Desktop/'+ user.strip() + '_email/'
else:
    detach_dir = 'C:\\Users\\'+os.getlogin()+'\\Desktop\\' + user.strip() + '_email\\'

attach_dir = detach_dir+"attachments"

if not os.path.exists(detach_dir):
    os.makedirs(detach_dir)

if not os.path.exists(attach_dir):
    os.makedirs(attach_dir)

blah = raw_input("Ready to backup gmail account for: "+user+". Backup will be located at: "+detach_dir+". Press enter to continue")


""" TODO: get the header instead of the whole message,
so we can check if we have the msg/attachment already before downloading
This will greatly improve performance (cache) """
#TODO: handle german characters (so all Unicode right?) -- error on 'C:\\Users\\abarnes\\barnes_d2@denison.edu_email\\attachments\\=?ISO-8859-1?Q?=D6sterrechische_Geschichte?=\r\n\t=?ISO-8859-1?Q?=2Eppt?='

for emailid in items:
    resp, data = m.fetch(emailid, "(RFC822)")
    raw_email = data[0][1]
    email_message = str(email.message_from_string(raw_email)).decode("quoted-printable")
    mail = email.message_from_string(raw_email)

    if (mail["Subject"]!=None):
        SUBJECT = mail["Subject"]
        SUBJECT = SUBJECT.strip()
        SUBJECT = replace_all(SUBJECT,["/","\\",":","<",">","?","|","*","\"",".","\r","\n","\t","-","="])
        
    subj_copy = SUBJECT
        
    save_string = str(detach_dir + SUBJECT + "_" + str(emailid) + ".eml")
    
    if not os.path.isfile(save_string):

        counter = 1
        while(True):
            try:
                os.path.getsize(save_string)
                #print("Successful getsize")
                break
            except OSError as e:
                if e.errno == 63:
                    save_string = save_string.replace(subj_copy, subj_copy[:len(subj_copy)-counter])
                    subj_copy = subj_copy[:len(subj_copy)-counter]
                    counter+=1
                    #print("COunter: "+str(counter))
                    #print("save_string:"+save_string)
                    continue
                else:
                    #resize should be done
                    break
        
        myfile = open(save_string, 'a')
        myfile.write(email_message)
        myfile.close()
        
        print("CREATED EMAIL FILE "+SUBJECT +" -------"+str(emailid))
    else:
        print("SKIPPED EMAIL FILE "+SUBJECT+"...already exists--"+str(emailid))

    if mail.get_content_maintype() != 'multipart':
        continue

    for part in mail.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue

        filename = part.get_filename()
        counter = 1

        if not filename:
            filename = 'part-%03d%s' % (counter, 'bin')
            counter += 1

        filename = replace_all(filename,["*"])

        att_path = os.path.join(attach_dir, filename)
        if not os.path.isfile(att_path) :
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()
            print("SAVED ATTACHMENT: " + filename + "from email: "+ emailid)
        else:
            print("SKIPPED ATTACHMENT: "+ filename + "----from email: "+ emailid+"...already exists in folder")

m.close()
m.logout
