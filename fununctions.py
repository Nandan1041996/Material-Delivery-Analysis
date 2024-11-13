import numpy as np
import pandas as pd
class DataEngineeringClass:

    def df_feature_engineering(self,vendor_material_df,no_of_order):
        
        vendor_material_df['Purchase Type'] = np.where(vendor_material_df['Purchasing Doc. Type']=='NB6','Capital','Revenue')
        print('vendor_material_df',vendor_material_df)
        final_df = vendor_material_df[['Vendor','Item','Purchasing Doc. Type','Purchase Type', 'Material',
                    'Material Group', 'Quantity Column','Order Unit', 'Planned Deliv. Time',
                    'Posting Date', 'Created on', 'Delivery date']]
        print(final_df.dtypes)
        final_df['Posting Date'] = pd.to_datetime(final_df['Posting Date'])
        final_df['Created on'] = pd.to_datetime(final_df['Created on'])
        final_df['Delivery date'] = pd.to_datetime(final_df['Delivery date'])
        
        final_df['Delay_not_Ontime'] = final_df['Delivery date']-final_df['Posting Date']
        final_df['Delay_not_Ontime'] = final_df['Delay_not_Ontime'].astype('str').apply(lambda x : int(x.split(sep=' ')[0]))
        # final_df['Delay_not_Ontime'] = final_df['Delay_not_Ontime'].apply(lambda x : int(x.split(sep=' ')[0]))
        final_df['Delivery_Status'] = final_df['Delay_not_Ontime'].apply(lambda x: 'Early' if x < 0 else ('OnTime' if x > 0 and x < 7 else 'Delay'))
    
        final_df['Average_Cycle_Time'] = final_df['Posting Date']-final_df['Created on']  #  
        final_df['Average_Cycle_Time'] = final_df['Average_Cycle_Time'].astype('str').apply(lambda x : int(x.split(sep = ' ')[0])).to_list()
        
        # string to number Conversion 
        Dilevary_Status_encoding = {'Early' : 0, 'OnTime' : 1, 'Delay' : 2}
        
        final_df['Delivery_Status'] = final_df['Delivery_Status'].map(Dilevary_Status_encoding)
    
        material_lst = self.filter_materials(final_df,no_of_order)
        print(material_lst)
        dataframe_lst = self.fiter_records(final_df,material_lst,no_of_order)
        
    
        final_df = pd.concat(dataframe_lst)
    
        text_list = self.get_vendor_information(final_df,no_of_order)
        print(text_list)
        final_result_df = pd.DataFrame(text_list)
    
        return final_result_df


    def fiter_records(self,final_df,material_lst,no_of_order = 25):
        '''This function is used to filter out Vendor wise material 
            order greate than no of order.

        Args:
        final_df([DataFrame]): Dataframe
        material_lst([List]) : Material List
        no_of_order ([Integer]) : Order count

        Return:
        df_lst([List]) : List contains dataframe list 
        '''
        df_lst =[]
        for vid in final_df['Vendor'].unique(): 
            for mat in material_lst:
                if  len(final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat)])>=no_of_order:  #25
                    df_lst.append(final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat)])
        return df_lst

    def filter_materials(self,final_df,no_of_order=25):
        '''This function is used to filter out materials which has order
            greater and equals to the no_of_order

        Args:
        final_df([DataFrame]) : Its dataframe on which operation will perform
        no_of_order([Integer]) : Number of Order

        Returns:
        material_lst([List]) : List 
        '''
        materal_count_dict = final_df['Material'].value_counts()

        material_lst = []
        for k,v in materal_count_dict.items():
            if v>=no_of_order:
                material_lst.append(k)
        return material_lst

    def get_vendor_information(self,final_df,no_of_order=25):
        '''This Function is used to determine information about vendor 
            like Vendor Rating  for Perticular material , Total Delivery of Material 
            done in Year, Expected Delivery Time in days , Planned Delivery Time In days
            Total Qty Produeced by Vendor, Qty Produced In Revenue and Capital,
            Produce Early and Delay Information etc.

        Args:
        final_df([DataFrame]) : Its DataFrame On which Operation is Performed 
        no_of_order([Integer]) : Number of Orders

        Returns:
        text_lst([List]) : This function returns List of Dictionary.
        '''
        text_lst = []
        for mat in final_df['Material'].unique():
            for vid in final_df['Vendor'].unique():   
                data_dict={}
                if len(final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat)])>=no_of_order:
                    
                    # Total Material Provide by Vendor 
                    Vid_Mat_Qty = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat)]['Quantity Column'].sum()
                    Vid_Mat_Qty = round(Vid_Mat_Qty,3)
                    Mat_Unit = final_df[(final_df['Material'] == mat)]['Order Unit'].unique()
                    
                    # to calculate percentage Pyrchase Doc Type wise
                    revenue_data = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Revenue')]
                    capital_data = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Capital')]
                    
                    # Delay Order
                    bad_Cap_len = len(final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat)& (final_df['Purchase Type'] == 'Capital') & (final_df['Delivery_Status'] == 2)])
                    bad_Rev_len = len(final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat)& (final_df['Purchase Type'] == 'Revenue') & (final_df['Delivery_Status'] == 2)])

                    # Early / Ontime Order
                    good_Rev_len = len(final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Revenue') & (final_df['Delivery_Status'].isin([0,1]))])
                    good_Cap_len = len(final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Capital') & (final_df['Delivery_Status'].isin([0,1]))])
                
                    #  Purchase time wise delivery time
                    dilivery_cap_time = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Capital')]['Planned Deliv. Time'].mean()
                    delivery_rev_time = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Revenue')]['Planned Deliv. Time'].mean()

                    data_dict.update({'Vendor':vid})
                    data_dict.update({'Material': mat})

                    data_dict.update({'Total Qty': Vid_Mat_Qty})
                    data_dict.update({'Material Unite': Mat_Unit[0]})
                    
                    if len(revenue_data) > 0:
                        # Revenue Qty total Sum
                        revenue_qty_sum = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Revenue')]['Quantity Column'].sum()
                        data_dict.update({'Total Revenue Qty': revenue_qty_sum})
                        data_dict.update({'Revenue Planned Delivery Time In Days': round(delivery_rev_time,0)})

                        # to get expected dilivery date for Revenue
                        Rev_Exp_Delivery_Days = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Revenue')]['Average_Cycle_Time'].mean()
                        data_dict.update({'Revenue Expected Dilivery Time In Days': round(Rev_Exp_Delivery_Days,0)})

                        # Rating for Revenue Delay- Early/Ontime 
                        Rev_rating_val  = round(good_Rev_len/len(revenue_data)*100,0)-round(bad_Rev_len/len(revenue_data)*100,0)
                        Rev_rating = ('A' if (Rev_rating_val >=75) else 'B' if (Rev_rating_val >=50 and Rev_rating_val <75) else 'C' if (Rev_rating_val >= 25 and Rev_rating_val <50) else 'D') 
                        
                        # data_string += '\nDelivery Details :'
                        data_dict.update({'Revenue Delay Order': bad_Rev_len})
                        data_dict.update({'Revenue Early/Ontime Order': good_Rev_len})
                        data_dict.update({'Revenue Delay Percentage': round(bad_Rev_len/len(revenue_data)*100,0)})
                        data_dict.update({'Revenue Early/Ontime Percentage': round(good_Rev_len/len(revenue_data)*100,0)})
                        data_dict.update({'Revenue Rating': Rev_rating})
                    
                    if len(revenue_data) == 0:
                        data_dict.update({'Total Revenue Qty': 0})
                        data_dict.update({'Revenue Planned Delivery Time In Days': 0})
                        data_dict.update({'Revenue Expected Dilivery Time In Days': 0})
                        data_dict.update({'Revenue Delay Order': 0})
                        data_dict.update({'Revenue Early/Ontime Order': 0})
                        data_dict.update({'Revenue Delay Percentage': 0})
                        data_dict.update({'Revenue Early/Ontime Percentage': 0})
                        data_dict.update({'Revenue Rating': 'NA'})
                        
                    if len(capital_data)> 0:
                        # Capital Qty total Sum
                        capital_qty_sum = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Capital')]['Quantity Column'].sum()
                        data_dict.update({'Total Capital Qty': capital_qty_sum})
                        data_dict.update({'Capital Planned Delivery Time In Days': round(dilivery_cap_time,0)})
                        # to get expected dilivery date for Capital
                        Cap_Exp_Delivery_Days = final_df[(final_df['Vendor'] == vid) & (final_df['Material'] == mat) & (final_df['Purchase Type'] == 'Capital')]['Average_Cycle_Time'].mean()
                        data_dict.update({'Capital Expected Dilivery Time In Days': round(Cap_Exp_Delivery_Days,0)})

                        # rating 
                        Cap_rating_val  =round(good_Cap_len/len(capital_data)*100,0)-round(bad_Cap_len/len(capital_data)*100,0)
                        Cap_rating = ('A' if (Cap_rating_val >=75) else 'B' if (Cap_rating_val >=50 and Cap_rating_val <75) else 'C' if (Cap_rating_val >= 25 and Cap_rating_val <50) else 'D') 
                        data_dict.update({'Capital Delay Order': bad_Cap_len})
                        data_dict.update({'Capital Early/Ontime Order': good_Cap_len})
                        data_dict.update({'Capital Delay Percentage': round(bad_Cap_len/len(capital_data)*100,0)})
                        data_dict.update({'Capital Early/Ontime Percentage': round(good_Cap_len/len(capital_data)*100,0)})
                        data_dict.update({'Capital Rating': Cap_rating})
                    if len(capital_data) == 0:
                        data_dict.update({'Total Capital Qty': 0})
                        data_dict.update({'Capital Planned Delivery Time In Days': 0})
                        data_dict.update({'Capital Expected Dilivery Time In Days': 0})
                        
                        data_dict.update({'Capital Delay Order': 0})
                        data_dict.update({'Capital Early/Ontime Order': 0})
                        data_dict.update({'Capital Delay Percentage': 0})
                        data_dict.update({'Capital Early/Ontime Percentage': 0})
                        data_dict.update({'Capital Rating': 'NA'})
                        
                    text_lst.append(data_dict)  
        return text_lst      
                            
