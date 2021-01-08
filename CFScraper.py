# ------------------------------------------------
# CONSTANTS FOR THE SCRAPER - CHANGE TO YOUR NEED
logging = False # Progress printing will be made to the console
save_to_pdf = False # Has not been fully implemented
debugging = False # Enabling this will only export 1 contact
auto_email = False  # Enabling this will auto email the csv file to a target email
# ------------------------------------------------

import requests
import argparse
import csv
import time
import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

class CFScraper:
    def __init__(self, logging=True, save_to_pdf=False):
        self.logging = logging
        self.save_to_pdf = save_to_pdf

    def scrape_authors(self, articles_by_author_link="https://canopyforum.org/articles-by-author/"):
        if self.logging:
            print("Collecting authors....")

        articles_by_date_page = requests.get(
            articles_by_author_link)
        soup = BeautifulSoup(articles_by_date_page.text, "html.parser")

        list_of_links = soup.find(class_="tag-groups-alphabetical-index")
        authors = list_of_links.find_all('a')

        return [(link.find("span").contents[0], link.get('href')) for link in authors]

    def scrape_author_links(self, author, author_link):
        if self.logging:
            print("Scraping {} link: {}".format(author, author_link))

        author_article = requests.get(author_link)
        soup = BeautifulSoup(author_article.text, "html.parser")
        articles_block = soup.find(id="main-core")
        articles = articles_block.find_all('div', class_="entry-content")

        links = []

        didFlag = False
        for link in articles:
            if (link is None or link == "") and not didFlag:
                if self.logging:
                    print("WARNING: " + str(author_link) +
                          " returned an invalid article link")
                    didFlag = True

            else:
                links.append(link.find('a').get('href'))

        other_pages = articles_block.find('a', class_="next")
        if other_pages is not None:
            links += self.scrape_author_links(author, other_pages.get('href'))
        if len(links) < 1 and self.logging:
            print("WARNING: " + author_link +
                  " returned an empty list of articles")
        return links

    def scrape_article(self, article_link):
        if self.logging:
            print("\tScraping article link: " + str(article_link))

        article = requests.get(article_link)
        soup = BeautifulSoup(article.text, "html.parser")

        entry_meta = soup.find(class_="entry-meta")
        if entry_meta is not None:
            try:
                title = entry_meta.find(class_="date").find("a")['title']
            except Exception as e:
                print(
                    "ERROR: could not get title for {} - got: {}".format(article_link, str(e)))
                title = "COULD NOT PARSE"
            try:
                published_date = entry_meta.find(
                    class_="date").find("time")['datetime']
            except Exception as e:
                print(
                    "ERROR: could not get published date for {} - got: {}".format(article_link, str(e)))
                published_date = "COULD NOT PARSE"
            try:
                tags = [tag.contents[0] for tag in entry_meta.find(
                    class_="tags").findAll("a")]
            except Exception as e:
                if self.logging:
                    print(
                        "ERROR: could not parse tags for {} - got: {}".format(article_link, str(e)))
                    tags = ["COULD NOT PARSE"]

                else:
                    if self.logging:
                        print(
                            "ERROR: could not get entry meta data for {} - got: {}".format(article_link, str(e)))
                    title, published_date, tags = "COULD NOT PARSE"

        try:
            cover_image = soup.find("meta", property="og:image")['content']
        except Exception as e:
            if self.logging:
                print(
                    "ERROR: could not parse cover image for {} - got: {}".format(article_link, str(e)))
                cover_image = "COULD NOT PARSE"

        if self.save_to_pdf:
            try:
                from weasyprint import HTML, CSS
                dec = []
                dec.append(soup.find("div", id="pre-header"))
                dec.append(soup.find("div", id="header"))
                dec.append(soup.find("div", id="sub-footer"))
                dec.append(soup.find("header"))
                dec.append(soup.find("header", class_="entry-header"))
                dec.append(soup.find("div", class_="sfsi_responsive_icons"))
                dec.append(soup.find("nav"))
                dec.append(soup.find("div", class_="wp-block-cover"))
                del soup.find(class_="has-drop-cap")["class"]
                for p in soup.findAll("p"):
                    del p["style"]
                dec += [spacer
                        for spacer in soup.findAll("div", class_="wp-block-spacer")]
                dec += [img
                        for img in soup.findAll("div", class_="wp-block-image")]
                dec += [quote
                        for quote in soup.findAll("figure", class_="wp-block-pullquote")]
                [item.decompose() for item in dec if item is not None]
                pdf_title = "<img src='https://canopyforum.org/wp-content/uploads/2019/08/cropped-header8-1.png' alt=''><hr>" + "<div class='pdftitle'><p><b>{}</b><br>By {}<br>{}</p></div>".format(title[1:title.index(
                    '” by')], title[title.index('” by ') + 5:], datetime.datetime.strptime(published_date[0:10], "%Y-%m-%d").strftime("%b. %d %Y"))
                soup_text = str(soup.prettify())
                soup_text = soup_text[:soup_text.index(
                    'entry-content">') + len('entry-content">')] + pdf_title + soup_text[soup_text.index('entry-content">') + len('entry-content">'):]

                closing = "<div><p><b>Bibliography/Citations:</b><br>Cite<br>Cite<br>Cite<br>DOI: [<a href='https://canopyforum.org/2020/10/23/reconciling-retribution-and-rehabilitation/'>https://canopyforum.org/2020/10/23/reconciling-retribution-and-rehabilitation/</a>]<br><br><i>Canopy Forum</i> is a publication of the Center for the Study of Law and Religion at Emory University (Atlanta, GA). Copyright 2020.</p></div>"

                soup_text = soup_text[:soup_text.index(
                    'class="wp-block-separator"') + len('class="wp-block-separator"> ')] + closing + soup_text[soup_text.index(
                        'class="wp-block-separator"') + len('class="wp-block-separator"> '):]
                html = HTML(string=soup_text,
                            base_url=".")
                css = CSS(
                    string='''
                        @page {
                            size: Letter !important;
                            margin: 0in -1in 0in -1in !important;
                        }

                        @body {
                            padding: none !important;
                            margin: none !important;
                        }

                      h1 { font-family: Garamond, Baskerville, Baskerville Old Face, Hoefler Text, Times New Roman, serif; font-size: 18px; font-style: normal; font-variant: normal; font-weight: 700; line-height: 18px; } h3 { font-family: Garamond, Baskerville, Baskerville Old Face, Hoefler Text, Times New Roman, serif; font-size: 14px; font-style: normal; font-variant: normal; font-weight: 700; line-height: 18px; } p { font-family: Garamond; font-size: 11px; font-style: normal; font-variant: normal; font-weight: 400; line-height: 18px; } blockquote { font-family: Garamond, Baskerville, Baskerville Old Face, Hoefler Text, Times New Roman, serif; font-size: 14px; font-style: normal; font-variant: normal; font-weight: 400; line-height: 18px; } pre { font-family: Garamond, Baskerville, Baskerville Old Face, Hoefler Text, Times New Roman, serif; font-size: 9px; font-style: normal; font-variant: normal; font-weight: 400; line-height: 18px; }

                       div .entry-content {
                            -webkit-columns: 200px 2;
                            /* Chrome, Safari, Opera */
                            -moz-columns: 200px 2;
                            /* Firefox */
                            columns: 200px 2;
                        }
                        .pdftitle {
                            color: red !important;
                            text-align: center !important;
                        }
                        p:not(.pdftitle){
                            color: black !important;
                            text-align: justify !important;
                            text-indent: 50px !imporant;
                        }

                        .wp-block-media-text{
                            width: inherit !important;;
                            grid-template-columns:15% auto !important;
                            text-align: left !important;
                        }
                        .wp-block-media-text__media{
                            display: block;
                            margin-left: auto;
                            margin-right: auto;
                            width: 100px;
                            padding-left: 35%;
                        }

                        ''')
                html.write_pdf("{}.pdf".format(title), stylesheets=[css])

            except Exception as e:
                print("ERROR: Tried saving: {} but got: {}".format(
                    article_link, str(e)))

        return [title, published_date, cover_image, article_link] + [tag for tag in tags]

    def export_articles(self, data, fname):
        if self.logging:
            print("EXPORTING TO {}.csv".format(fname))

        file_name = fname + '.csv'
        fields = ['AUTHOR NAME', 'ARTICLE TITLE', 'DATE PUBLISHED',
                  'COVER IMAGE', 'ARTICLE LINK', 'TAGS']
        with open(file_name, 'w') as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(data)

    def toggle_log(self, toggle):
        self.logging = toggle

# libraries to be imported
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import argparse


class Save:
    def __init__(self, fromaddr, password):
        print("Trying to login using GMAIL: {} and Password: {}".format(fromaddr, password))
        try:
            # creates SMTP session
            s = smtplib.SMTP('smtp.gmail.com', 587)

            # start TLS for security
            s.starttls()

            # Authentication
            s.login(fromaddr, password)
            s.quit()
            print("Login Successful - proceeding to scraper!")
        except Exception as e:
            print("Got error: {}".format(str(e)))
            print("\n\nTip: Log into the gmail from your browser, go to Manage Your Google Account, Select Security, and ensure that Less Secure App Access is enabled. For security reasons, ensure the scraper google account is being used.")
            exit()

    def sendToMail(self, fromaddr, password, toaddr, filename):
        try:
            fromaddr = fromaddr
            toaddr = toaddr

            # instance of MIMEMultipart
            msg = MIMEMultipart()

            # storing the senders email address
            msg['From'] = fromaddr

            # storing the receivers email address
            msg['To'] = toaddr

            # storing the subject
            msg['Subject'] = "Canopy Forum Scraper Data"

            # string to store the body of the mail
            body = ""

            # attach the body with the msg instance
            msg.attach(MIMEText(body, 'plain'))

            # open the file to be sent
            filename = "cf_data.csv"
            attachment = open(filename, "rb")

            # instance of MIMEBase and named as p
            p = MIMEBase('application', 'octet-stream')

            # To change the payload into encoded form
            p.set_payload((attachment).read())

            # encode into base64
            encoders.encode_base64(p)

            p.add_header('Content-Disposition',
                         "attachment; filename= %s" % filename)

            # attach the instance 'p' to instance 'msg'
            msg.attach(p)

            # creates SMTP session
            s = smtplib.SMTP('smtp.gmail.com', 587)

            # start TLS for security
            s.starttls()

            # Authentication
            s.login(fromaddr, password)

            # Converts the Multipart msg into a string
            text = msg.as_string()

            # sending the mail
            s.sendmail(fromaddr, toaddr, text)

            # terminating the session
            s.quit()
            print("Emailed scrapped data to {} successfully!".format(toaddr))

        except Exception as e:
            print("Got error while trying to send email: {}".format(str(e)))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--email', '-e', type=str,
                        help="The scraper's email - sender's email", default=" ")

    parser.add_argument('--to', '-t', type=str,
                        help="The receivers's email - sender's email", default=" ")

    parser.add_argument('--password', '-p', type=str,
                        help="The password for the scraper's email provided", default=" ")

    parser.add_argument('--filename', '-f', type=str,
                        help="The file name of the data to send (do not include .csv)", default="cf_data")

    args = parser.parse_args()

    if auto_email and (args.email == " " or args.password == " " or args.to == " "):
        raise ValueError("Email, To, and Password must be provided! Use --email, --password, and --to to provide the sender email, password, and receiver email. You can also use --help for more info.")
        exit()
    elif not auto_email and (args.email != " " or args.password != " " or args.to != " "):
        print("You provided email parameters, but the auto_email flag is disabled in the script! Enable it to email the exported data!")
        exit()

    save = None
    if auto_email:
        save = Save(args.email, args.password)
    scraper = CFScraper(logging, save_to_pdf)
    authors = scraper.scrape_authors()
    articles = []

    for i in tqdm(range(len(authors))):
        for article_link in scraper.scrape_author_links(authors[i][0], authors[i][1]):
            articles.append([authors[i][0]] +
                            [item for item in scraper.scrape_article(article_link)])
            time.sleep(2)
            if debugging:
                break
        if debugging:
            break

    scraper.export_articles(articles, args.filename)
    if auto_email:
        save.sendToMail(args.email, args.password, args.to, args.filename)
