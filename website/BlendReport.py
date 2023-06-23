import pandas as pd
from fpdf import FPDF
from .models import PowderBlends, PowderBlendParts, InventoryVirginBatch, MaterialsTable


class BlendReport:
    def __init__(self, blend):
        self.blend = blend
        self.blend_data = None
        self.total_weight = None
        self.grouped = None
        self.maj = None
        self.product = None
        self.maj_batch = None
        self.maj_po = None
        self.maj_prod = None
        self.maj_lot = None
        self.count_avg = None
        self.count_max = None
        self.blend_summary = None
        self.blend_breakdown = None
    
    def load_data(self):
        self.blend_data = (
            PowderBlendParts.query.join(InventoryVirginBatch, PowderBlendParts.PartBatchID == InventoryVirginBatch.BatchID)
            .join(MaterialsTable, PowderBlendParts.MaterialID == MaterialsTable.MaterialID)
            .filter(PowderBlendParts.BlendID == self.blend)
            .add_columns(
                PowderBlendParts.PartBlendID, 
                PowderBlendParts.PartBatchID, 
                InventoryVirginBatch.VirginPO, 
                InventoryVirginBatch.VirginLot, 
                MaterialsTable.SupplierProduct, 
                PowderBlendParts.PartFraction, 
                PowderBlendParts.SieveCount,
            )
            .all()
        )
        self.total_weight = (
            PowderBlends.query.filter_by(BlendID=self.blend)
            .with_entities(PowderBlends.TotalWeight)
            .scalar()
        )
    
    def process_blend(self):
        blend_data_df = pd.DataFrame(
            self.blend_data, 
            columns=[
                'PartBlendID', 
                'PartBatchID', 
                'VirginPO', 
                'VirginLot', 
                'SupplierProduct', 
                'PartFraction', 
                'SieveCount',
            ],
        )
        blend_data_df.sort_values(by=['PartFraction'], ascending=False, inplace=True)
        
        self.grouped = (
            blend_data_df.groupby(by=['PartBatchID'], as_index=False)
            .sum()[['PartBatchID', 'PartFraction']]
        )
        self.grouped.sort_values(by=['PartFraction'], ascending=False, inplace=True)
        
        self.maj = self.grouped.iloc[0]
        self.maj_batch = self.maj['PartBatchID']
        self.maj_po = self.blend_data[0][2]
        self.maj_prod = self.blend_data[0][4]
        self.maj_lot = str(self.blend_data[0][3])
        self.count_avg = round((blend_data_df['PartFraction'] * blend_data_df['SieveCount']).sum())
        self.count_max = blend_data_df['SieveCount'].max()
        
        summary_dict = {
            'Blend': self.blend, 
            'Product ID': self.product, 
            'Total Weight (kg)': self.total_weight, 
            'Majority Batch ID': self.maj_batch,
            'Majority Batch PO': self.maj_po, 
            'Majority Batch Product': self.maj_prod, 
            'Majority Batch Lot': self.maj_lot,
            'Average Sieve Count': self.count_avg,
            'Maximum Sieve Count': self.count_max,
        }
        self.blend_summary = pd.DataFrame(summary_dict, index=['Value']).T
        self.blend_summary.fillna(value='---', inplace=True)
        
        self.blend_breakdown = blend_data_df.head(30)
        self.blend_breakdown['Percent'] = self.blend_breakdown['PartFraction'] * 100
        self.blend_breakdown = self.blend_breakdown[['PartBatchID', 'VirginPO', 'VirginLot', 'SupplierProduct', 'Percent', 'SieveCount']]
        self.blend_breakdown.rename(columns={'PartBatchID': 'Batch ID', 
                                            'VirginPO': 'Virgin PO', 
                                            'VirginLot': 'Virgin Lot', 
                                            'SupplierProduct': 'Product',
                                            'SieveCount': 'Sieve Count',
                                            }, inplace=True)
        other_per = 100.00001 - self.blend_breakdown['Percent'].sum()
        self.blend_breakdown.loc[self.blend_breakdown.shape[0]] = ['', '', 'Other', '', other_per, '']
        self.blend_breakdown['Percent'] = self.blend_breakdown['Percent'].map('{:.1f}%'.format)
        self.blend_breakdown.fillna(value='---', inplace=True)
    
    def generate_report_pdf(self):
        blend_summary_html = self.blend_summary.to_html(index=True, header=False, classes='dataframe') \
            .replace('<th', '<th style="text-align: right;"')
        blend_breakdown_html = self.blend_breakdown.to_html(index=False, justify='left', classes='dataframe') \
            .replace('Other', '<b>Other</b>')

        report_html = f'''
            <html>
            <head>
                <style>
                    h1 {{
                        font-family: verdana;
                        text-align: center;
                        font-size: 24px;
                        font-weight: bold;
                    }}
                    p {{
                        font-family: verdana;
                        font-size: 12px;
                        margin-bottom: 10px;
                    }}
                    table {{
                        font-family: verdana;
                        margin-left: auto;
                        margin-right: auto;
                    }}
                    th {{
                        border: 0px;
                        padding-right: 25px
                    }}
                    tr {{
                    }}
                    td {{
                        border: 0px;
                        padding-right: 20px
                    }}
                </style>
            </head>
            <body>
                <h1>DMLM Material Blend Report</h1>
                <br>
                {blend_summary_html}
                <br>
                {blend_breakdown_html}
            </body>
            </html>
        '''

        return report_html
