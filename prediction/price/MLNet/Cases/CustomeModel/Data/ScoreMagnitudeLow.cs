using Microsoft.ML.Data;

namespace CustomeModel.Data
{
    class ScoreMagnitudeLow
    {
        [ColumnName("companyID"), LoadColumn(0)]
        public float CompanyID { get; set; }


        [ColumnName("magnitude"), LoadColumn(7)]
        public float Magnitude { get; set; }


        [ColumnName("score"), LoadColumn(13)]
        public float Score { get; set; }


        [ColumnName("low"), LoadColumn(6)]
        public float Low { get; set; }
    }
}
