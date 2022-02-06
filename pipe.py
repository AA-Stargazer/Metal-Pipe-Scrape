import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy.shell import inspect_response

from scrapy.selector import Selector


class PipeSpider(scrapy.Spider):
    name = 'pipe'
    # allowed_domains = ['www.onlinemetals.com/en/buy/pipe']
    # start_urls = ['https://www.onlinemetals.com/en/buy/pipe']

    def __init__(self):
        self.link_list = []

    def start_requests(self):
        yield SeleniumRequest(url='https://www.onlinemetals.com/en/buy/pipe',
        callback=self.controller,
        wait_time=3,
        wait_until=EC.presence_of_element_located((By.XPATH, '//div[@class="banner__component banner"]/a/img'))
        )
    
    def controller(self, response):
        response0 = response
        self.driver = response.meta['driver']
        response = Selector(text=self.driver.page_source)

        links = response.xpath('//div[@class=" col-sm-12 similar-product__item product-order__list "]//div[contains(@class, "similar-product__item_title")]/h4//a/@href').getall()
        for link in links:
            self.link_list.append(link)

        next_page = response.xpath('//li[@id="pagination-right"]/a/@href').get()
        if next_page:
            yield SeleniumRequest(url='https://www.onlinemetals.com' + next_page,
            callback=self.controller,
            wait_time=3,
            wait_until=EC.presence_of_element_located((By.XPATH, '//div[@class="banner__component banner"]/a/img'))
            )
        else:
            for link in self.link_list:
                self.driver.get('https://www.onlinemetals.com' + link)
                yield self.parse_item()
                    # yield SeleniumRequest(url='https://www.onlinemetals.com' + link,
                # callback=self.controller,
                # wait_time=3,
                # wait_until=EC.presence_of_element_located((By.XPATH, '//div[@class="banner__component banner"]/a/img'))
                # )
        
    def dencode(self, string):
        string = string.strip().replace('\n', '').encode().decode('utf-8', 'ignore').replace("\u00a0"," ")
        return string



    def parse_item(self):
        print('\n\n\nsdrsdfgsdfg\n\n\n')
        response = Selector(text=self.driver.page_source)
        # inspect_response(response, self)
        #Table Dimension Name
        # alloy = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Alloy")]/following-sibling::td/text()').get()
        # production_method = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Production Method")]/following-sibling::td/text()').get()
        # nominal = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Nominal")]/following-sibling::td/text()').get()
        # schedule = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Schedule")]/following-sibling::td/text()').get()
        # outer_diameter = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Outer Diameter")]/following-sibling::td/text()').get()
        # wall = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Wall")]/following-sibling::td/text()').get()
        # inner_diameter = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Inner Diameter")]/following-sibling::td/text()').get()
        # max_length = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Max Length")]/following-sibling::td/text()').get()
        # material = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Material")]/following-sibling::td/text()').get()
        # shape = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Shape")]/following-sibling::td/text()').get()
        # custom_cut_warehouse = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td[contains(text(), "Custom Cut Warehouse")]/following-sibling::td/text()').get()
        # mtr_availability = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//td/a[contains(text(), "MTR")]/parent::td/following-sibling::td/text()').get()
        dimension_dict = {}
        dimension_info_table = response.xpath('//table//h3[contains(text(), "Dimension Name")]//ancestor::table//tr')[1:]
        for tr in dimension_info_table:
            tds = tr.xpath('.//td')
            if tds[0].xpath('.//a/text()').get():
                dimension_dict['MTR Availability'] = self.dencode(tds[1].xpath('.//text()').get())
            else:
                dimension_dict[self.dencode(tds[0].xpath('.//text()').get())] = self.dencode(tds[1].xpath('.//text()').get())

        # Table Chemistry Information
        chem_info_dict = {}
        chem_info_table = response.xpath('//table//h3[contains(text(), "Chemistry Information")]//ancestor::table//tr')[2:]
        for tr in chem_info_table:
            tds = tr.xpath('.//td/text()').getall()
            chem_info_dict[self.dencode(tds[0])] = self.dencode(tds[1])

        # Table Mechanical Properties
        mechanical_info_dict = {}
        mechanical_info_table = response.xpath('//table//h3[contains(text(), "Mechanical Properties")]//ancestor::table//tr')[2:]
        if mechanical_info_table:
            for tr in mechanical_info_table:
                tds = tr.xpath('.//td/text()').getall()
                mechanical_info_dict[self.dencode(tds[0])] = self.dencode(tds[1])

        # Table Weight/Lineal Foot
        try:
            weight_lineal_foot = self.dencode(response.xpath('//table//h3[contains(text(), "Weight/Lineal Foot")]//ancestor::table//tr[last()]/td/text()').get())
        except:
            weight_lineal_foot = ''

        price = self.dencode(response.xpath('//div[@class="item-price"]/div[@id="selectedVariantPdpPriceValue"]/@data-product-price').get())

        item = {
            'Title': self.dencode(response.xpath('string(//h1)').get()).split(' -Part #: ')[0],
            'Price': f'${price} per feet',
            'Part Number': '#' + self.dencode(response.xpath('string(//h1)').get()).split(' -Part #: ')[1],
            'Dimensional Information': dimension_dict,
            'Chemistry Information': chem_info_dict,
            'Mechanical Properties': mechanical_info_dict,
            'Weight/Lineal Foot': weight_lineal_foot,
            'URL': self.driver.current_url
        }
        return item
