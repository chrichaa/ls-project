import feedparser

def main():
    xml = feedparser.parse("http://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313.TR10.TRC2.A0.H0.Xxeon.TRS2&_nkw=xeon&_sacat=0&_rss=1")

    for post in xml.entries:
        print post.title

main()