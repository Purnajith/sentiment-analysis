using Microsoft.ML.Data;

namespace CustomeModel.Data
{
    class ScoreMagnitudeHigh
    {
        [ColumnName("companyID"), LoadColumn(0)]
        public float CompanyID { get; set; }


        [ColumnName("magnitude"), LoadColumn(7)]
        public float Magnitude { get; set; }


        [ColumnName("score"), LoadColumn(13)]
        public float Score { get; set; }


        [ColumnName("high"), LoadColumn(5)]
        public float High { get; set; }
    }
}
