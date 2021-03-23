import scrapy
import csv

class NecklaceSetsList(scrapy.Spider):
    name="NecklaceSetsList"

    allowed_domains = ['houseofindya.com']

    '''
    The url leading to the list of necklace sets.
    '''
    start_urls = [
        'https://www.houseofindya.com/zyra/necklace-sets/cat'
    ]


    def parse_item(self, response):
        '''
        Description:
            The description has two components, basic description and style tip. Between these two we have 2 <br> tags.
            For some products we had a empty <p></p> tags in the middle of the description.
            
            Description html content is one of these two types - the if condition in the line 36 deals with this
            <p>                                         |   <p>
            "Basic description content" - node[1]       |   "Basic description content" - node[1]   
            <p></p>                       node[2]       |   <br>                          node[2]
            <br>                          node[3]       |   <br>                          node[3]
            <br>                          node[4]       |   "Style tip content"           node[4]
            "Style tip content"           node[5]       |   </p>
            </p>                                        |
        '''

        description = response.xpath("//div[@class='prodecbox current']//p//node()").extract_first()

        if response.xpath("//div[@class='prodecbox current']//p//node()[5]").extract_first() != None :
            description = description + response.xpath("//div[@class='prodecbox current']//p//node()[5]").extract_first()
        else:
            description = description + response.xpath("//div[@class='prodecbox current']//p//node()[4]").extract_first()

        '''
        Price:
            Locate the position of the discount price or the actual price using the xpath.
        '''
        actual_price = response.xpath("//div[@class='prodRight']/h4/*/text()").extract_first()
        discount_price = response.xpath(" //div[@class='prodRight']/h4/span[2]/text()").extract_first()

        '''
        Images:
            In the product detailed page, we have 4 images of the necklace set. 
            We are looping through all of the images using the xpath to locate the images in the page. 
        '''
        image_urls = []

        for image_url in response.xpath("//div[@class='prodLeft']/div[@id='productsections']/ul[@class='sliderBox']/*"):
            image_urls.append(image_url.xpath('.//a/@data-image').extract_first())

        '''
        Write the extracted description, actual price, discounted price, image urls to json file and the csv file.
        '''
        yield {
            'Description': description,
            'Actual_price': actual_price,
            'Discount_price': discount_price,
            'Image_urls': image_urls
            }
        with open('data.csv', 'a', newline='') as file:
            adding_row = csv.writer(file)
            adding_row.writerow([description, actual_price, discount_price,image_urls])



    def parse(self, response):
        '''
        Opening the csv file in write mode to write all the details of the neckalace sets - description, discount & actual prices, image urls
        '''
        with open('data.csv', 'w', newline='') as file:
            adding_row = csv.writer(file)
            adding_row.writerow(['Description', 'Actual_price', 'Discount_price', 'Image_urls'])

        '''
        In the url that shows the list of necklace sets, we are pointing the xpath to JsonProductList, that has the product list. 
        We are iterating through each of the products, and taking the url that leads to the detailed product view url using .//@data-url.
        We are sending this url as an argument to the parse_item function
        '''
        for necklace_set in response.xpath("//ul[@id='JsonProductList']/*"):
            yield scrapy.Request(necklace_set.xpath('.//@data-url').extract_first(),callback=self.parse_item)