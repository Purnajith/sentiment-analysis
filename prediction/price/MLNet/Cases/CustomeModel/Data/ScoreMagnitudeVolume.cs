using Microsoft.ML.Data;

namespace CustomeModel.Data.ScoreMagnitudeVolume
{
    class ScoreMagnitudeVolume
    {
        [ColumnName("companyID"), LoadColumn(1)]
        public float CompanyID { get; set; }


        [ColumnName("magnitude"), LoadColumn(10)]
        public float Magnitude { get; set; }


        [ColumnName("score"), LoadColumn(18)]
        public float Score { get; set; }


        [ColumnName("volume"), LoadColumn(20)]
        public float Volume { get; set; }
    }
}
