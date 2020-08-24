// This file was auto-generated by ML.NET Model Builder. 

using Microsoft.ML.Data;

namespace AllSAColumnToVolumeML.Model
{
    public class ModelInput
    {
        [ColumnName("companyID"), LoadColumn(0)]
        public float CompanyID { get; set; }


        [ColumnName("cseEndTime"), LoadColumn(1)]
        public float CseEndTime { get; set; }


        [ColumnName("cseEndTimeFull"), LoadColumn(2)]
        public string CseEndTimeFull { get; set; }


        [ColumnName("cseStartTime"), LoadColumn(3)]
        public float CseStartTime { get; set; }


        [ColumnName("cseStartTimeFull"), LoadColumn(4)]
        public string CseStartTimeFull { get; set; }


        [ColumnName("high"), LoadColumn(5)]
        public float High { get; set; }


        [ColumnName("low"), LoadColumn(6)]
        public float Low { get; set; }


        [ColumnName("magnitude"), LoadColumn(7)]
        public float Magnitude { get; set; }


        [ColumnName("polarity"), LoadColumn(8)]
        public float Polarity { get; set; }


        [ColumnName("postEndRange"), LoadColumn(9)]
        public float PostEndRange { get; set; }


        [ColumnName("postEndRangeFull"), LoadColumn(10)]
        public string PostEndRangeFull { get; set; }


        [ColumnName("postStartRange"), LoadColumn(11)]
        public float PostStartRange { get; set; }


        [ColumnName("postStartRangeFull"), LoadColumn(12)]
        public string PostStartRangeFull { get; set; }


        [ColumnName("score"), LoadColumn(13)]
        public float Score { get; set; }


        [ColumnName("subjectivity"), LoadColumn(14)]
        public float Subjectivity { get; set; }


        [ColumnName("volume"), LoadColumn(15)]
        public float Volume { get; set; }


    }
}