from lxml import html
import requests
#import isbnlib
import re
import time

def getAmznPageByISBN( isbn ):
    # convert isbn13 to isbn 10
    #isbn10 = isbnlib.to_isbn10(isbn)
    print("ISBN: " + isbn)

    # append to https://www.amazon.com/gp/product/
    url = 'https://www.amazon.com/gp/product/' + isbn
    print("Found book at " + url + "!")

    # get Amazon page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }
    tries = 1
    page = requests.get(url,headers=headers)
    while not page.status_code==requests.codes.ok and tries < 10:
        time.sleep(1)
        page = requests.get(url)
        print ( "Tries = " + str(tries) )
        tries = tries + 1

    tree = html.fromstring( page.text )
    # tree = html.parse(url)

    return tree


def getProductDimensions( tree ):
    # find product name
    title =  tree.xpath('//h1[@id="title"]/span[@id="productTitle"]/text()')

    # find product dimensions
    dims =  tree.xpath('//li/b[contains(text(),"Product Dimensions:")]/following-sibling::text()')
    
    sizes = re.findall(r'\d+\.\d+|\d+',dims[0])
    sWidth = 'NaN'
    sHeight = 'NaN'
    if(sizes):
        sWidth = min(sizes)
        sHeight = max(sizes)
    # find page number and if it's paperback or hardcover
    bookType = 'None'
    pageNumbers = '0'
    hardcover = tree.xpath('//li/b[contains(text(),"Hardcover:")]/following-sibling::text()')
    paperback = tree.xpath('//li/b[contains(text(),"Paperback:")]/following-sibling::text()')

    if paperback:
        bookType = 'Paperback'
        pageNumbers = re.findall(r'\d+',paperback[0])
    elif hardcover:
        bookType = 'Hardcover'
        pageNumbers = re.findall(r'\d+',hardcover[0])
 
    print (sizes)
    print ( title[0] )
    print ( bookType + ": " + pageNumbers[0] )
    print ("Spine width is " + sWidth)
    return title[0],sWidth,sHeight


def getBookInfo( isbn ):
    # tree = getAmznPageByISBN( '9780830844111' )
    #tree = getAmznPageByISBN( '9780545010221' )
    tree = getAmznPageByISBN(isbn)
    author = tree.xpath('//*[contains(@class, "a-link-normal contributorNameID")]/text()')

    #bookDescription = tree.xpath('//div[contains(@id, "bookDescription_feature_div")]//div[contains(@id,"iframeContent")]')
    #bookDescription = tree.xpath("//div[contains(@id, 'bookDescription_feature_div')]//div[contains(@id,'iframeContent')]")
    bookDescription = tree.xpath("//div[@id='bookDescription_feature_div']//div[@id='bookDesc_iframe_wrapper']")
    #bookDescription = tree.xpath('//iframe')
    #print bookDescription[0].attrib.get('src')
    
    # return getProductDimensions( tree );
    print author
    print bookDescription
    for name,value in bookDescription[0].items():
        print('%s = %r' % (name,value))
    
def main():
    #tree = getAmznPageByISBN( '0830844112' )
    getBookInfo( '0830844112' );

if __name__ == "__main__":
    main()
