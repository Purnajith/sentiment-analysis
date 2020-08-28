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

    /*
    public class ModelInput
    {
        [ColumnName("code"), LoadColumn(0)]
        public string Code { get; set; }


        [ColumnName("companyID"), LoadColumn(1)]
        public float CompanyID { get; set; }


        [ColumnName("cseEndTime"), LoadColumn(2)]
        public float CseEndTime { get; set; }


        [ColumnName("cseEndTimeDate"), LoadColumn(3)]
        public string CseEndTimeDate { get; set; }


        [ColumnName("cseEndTimeFull"), LoadColumn(4)]
        public string CseEndTimeFull { get; set; }


        [ColumnName("cseStartTime"), LoadColumn(5)]
        public float CseStartTime { get; set; }


        [ColumnName("cseStartTimeDate"), LoadColumn(6)]
        public string CseStartTimeDate { get; set; }


        [ColumnName("cseStartTimeFull"), LoadColumn(7)]
        public string CseStartTimeFull { get; set; }


        [ColumnName("high"), LoadColumn(8)]
        public float High { get; set; }


        [ColumnName("low"), LoadColumn(9)]
        public float Low { get; set; }


        [ColumnName("magnitude"), LoadColumn(10)]
        public float Magnitude { get; set; }


        [ColumnName("polarity"), LoadColumn(11)]
        public float Polarity { get; set; }


        [ColumnName("postEndRange"), LoadColumn(12)]
        public float PostEndRange { get; set; }


        [ColumnName("postEndRangeDate"), LoadColumn(13)]
        public string PostEndRangeDate { get; set; }


        [ColumnName("postEndRangeFull"), LoadColumn(14)]
        public string PostEndRangeFull { get; set; }


        [ColumnName("postStartRange"), LoadColumn(15)]
        public float PostStartRange { get; set; }


        [ColumnName("postStartRangeDate"), LoadColumn(16)]
        public string PostStartRangeDate { get; set; }


        [ColumnName("postStartRangeFull"), LoadColumn(17)]
        public string PostStartRangeFull { get; set; }


        [ColumnName("score"), LoadColumn(18)]
        public float Score { get; set; }


        [ColumnName("subjectivity"), LoadColumn(19)]
        public float Subjectivity { get; set; }


        [ColumnName("volume"), LoadColumn(20)]
        public float Volume { get; set; }


    }
    */
}
