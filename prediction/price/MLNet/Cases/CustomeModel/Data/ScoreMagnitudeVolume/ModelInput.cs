using Microsoft.ML.Data;

namespace CustomeModel.Data.ScoreMagnitudeVolume
{
    class ModelInput
    {
        [ColumnName("companyID"), LoadColumn(0)]
        public float CompanyID { get; set; }


        [ColumnName("magnitude"), LoadColumn(7)]
        public float Magnitude { get; set; }


        [ColumnName("score"), LoadColumn(13)]
        public float Score { get; set; }


        [ColumnName("volume"), LoadColumn(15)]
        public float Volume { get; set; }
    }
}
