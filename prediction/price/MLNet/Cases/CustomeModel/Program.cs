using System;
using System.IO;
using CustomeModel.Data;
using CustomeModel.Data.ScoreMagnitudeVolume;
using Microsoft.ML;
using Microsoft.ML.Trainers.FastTree;

namespace CustomeModel
{
    class Program
    {

        static readonly string basePath = @"C:\Users\purna\source\repos\Purnajith\sentiment-analysis\prediction\price\";
        static readonly string casePath = @"MLNet\Cases\CustomeModel\Data\ScoreMagnitudeVolume";

        static readonly string _trainDataPath = Path.Combine(basePath, "arrangedData-train.csv");
        static readonly string _testDataPath = Path.Combine(basePath, "arrangedData-test.csv");
        static readonly string _modelPath = Path.Combine(basePath, casePath, "Model.zip");

        /*https://docs.microsoft.com/en-us/dotnet/machine-learning/tutorials/predict-prices*/
        static void Main(string[] args)
        {
            MLContext mlContextVolume = new MLContext(seed: 0);
            MLContext mlContextHigh = new MLContext(seed: 0);
            MLContext mlContextLow = new MLContext(seed: 0);
            var modelVolume = TrainVolume(mlContextVolume, _trainDataPath);
            var modelHigh = TrainHigh(mlContextHigh, _trainDataPath);
            var modelLow = TrainLow(mlContextLow, _trainDataPath);

            Evaluate<ScoreMagnitudeVolume>(mlContextVolume, modelVolume);
            Evaluate<ScoreMagnitudeHigh>(mlContextHigh, modelHigh);
            Evaluate<ScoreMagnitudeLow>(mlContextLow, modelLow);

            TestSinglePrediction(mlContextVolume,
                                    mlContextHigh,
                                    mlContextLow,
                                    modelVolume,
                                    modelHigh,
                                    modelLow);
        }

        public static ITransformer TrainVolume(MLContext mlContext, string dataPath)
        {
            IDataView dataView = mlContext.Data.LoadFromTextFile<ScoreMagnitudeVolume>(dataPath, hasHeader: true, separatorChar: ',');

            // Data process configuration with pipeline data transformations 
            var dataProcessPipeline = mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "polarity", "score", "subjectivity" });
            var pipeline = mlContext.Transforms.CopyColumns(outputColumnName: "Label", inputColumnName: "volume")
                .Append(mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "score" })
                .Append(mlContext.Regression.Trainers.FastTreeTweedie(new FastTreeTweedieTrainer.Options() { NumberOfLeaves = 17, MinimumExampleCountPerLeaf = 1, NumberOfTrees = 100, LearningRate = 0.3504487f, Shrinkage = 0.09932277f, LabelColumnName = "volume", FeatureColumnName = "Features" })));

            var model = pipeline.Fit(dataView);

            return model;
        }

        public static ITransformer TrainHigh(MLContext mlContext, string dataPath)
        {
            IDataView dataView = mlContext.Data.LoadFromTextFile<ScoreMagnitudeHigh>(dataPath, hasHeader: true, separatorChar: ',');

            // Data process configuration with pipeline data transformations 
            var dataProcessPipeline = mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "polarity", "score", "subjectivity" });
            var pipeline = mlContext.Transforms.CopyColumns(outputColumnName: "Label", inputColumnName: "high")
                .Append(mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "score" })
                .Append(mlContext.Regression.Trainers.FastTreeTweedie(new FastTreeTweedieTrainer.Options() { NumberOfLeaves = 17, MinimumExampleCountPerLeaf = 1, NumberOfTrees = 100, LearningRate = 0.3504487f, Shrinkage = 0.09932277f, LabelColumnName = "high", FeatureColumnName = "Features" })));

            var model = pipeline.Fit(dataView);

            return model;
        }

        public static ITransformer TrainLow(MLContext mlContext, string dataPath)
        {
            IDataView dataView = mlContext.Data.LoadFromTextFile<ScoreMagnitudeLow>(dataPath, hasHeader: true, separatorChar: ',');

            // Data process configuration with pipeline data transformations 
            var dataProcessPipeline = mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "polarity", "score", "subjectivity" });
            var pipeline = mlContext.Transforms.CopyColumns(outputColumnName: "Label", inputColumnName: "low")
                .Append(mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "score" })
                .Append(mlContext.Regression.Trainers.FastTreeTweedie(new FastTreeTweedieTrainer.Options() { NumberOfLeaves = 17, MinimumExampleCountPerLeaf = 1, NumberOfTrees = 100, LearningRate = 0.3504487f, Shrinkage = 0.09932277f, LabelColumnName = "low", FeatureColumnName = "Features" })));

            var model = pipeline.Fit(dataView);

            return model;
        }

        private static void Evaluate<T>(MLContext mlContext, ITransformer model)
        {
            
            IDataView dataView = mlContext.Data.LoadFromTextFile<T>(_testDataPath, hasHeader: true, separatorChar: ',');

            var predictions = model.Transform(dataView);

            var metrics = mlContext.Regression.Evaluate(predictions, "Label", "Score");

            Console.WriteLine();
            Console.WriteLine($"*************************************************");
            Console.WriteLine($"*       Model quality metrics evaluation         ");
            Console.WriteLine($"*------------------------------------------------");

            Console.WriteLine($"*       RSquared Score:      {metrics.RSquared:0.##}");

            Console.WriteLine($"*       Root Mean Squared Error:      {metrics.RootMeanSquaredError:#.##}");
        }

        private static void TestSinglePrediction(MLContext mlContextVolume,
                                                   MLContext mlContextHigh,
                                                   MLContext mlContextLow,
                                                   ITransformer modelVolume, 
                                                   ITransformer modelHigh, 
                                                   ITransformer modelLow)
        {
            
            var predictionFunctionVolume = mlContextVolume.Model.CreatePredictionEngine<ScoreMagnitudeVolume, ModelOutput>(modelVolume);
            var predictionFunctionHigh = mlContextHigh.Model.CreatePredictionEngine<ScoreMagnitudeHigh, ModelOutput>(modelHigh);
            var predictionFunctionLow = mlContextLow.Model.CreatePredictionEngine<ScoreMagnitudeLow, ModelOutput>(modelLow);


            int companyID = -1;
            float score = 0;
            float magnitiude = 0;

            Console.WriteLine("CompanyID:");
            companyID = int.Parse(Console.ReadLine());

            Console.WriteLine("Score:");
            score = float.Parse(Console.ReadLine());

            Console.WriteLine("Magnitiude:");
            magnitiude = float.Parse(Console.ReadLine());

            // Create single instance of sample data from first line of dataset for model input
            ScoreMagnitudeVolume sampleDataVolume = new ScoreMagnitudeVolume()
            {
                CompanyID = companyID,
                Magnitude = magnitiude,
                Score = score,
            };

            ScoreMagnitudeHigh sampleDataHigh = new ScoreMagnitudeHigh()
            {
                CompanyID = companyID,
                Magnitude = magnitiude,
                Score = score,
            };

            ScoreMagnitudeLow sampleDataLow = new ScoreMagnitudeLow()
            {
                CompanyID = companyID,
                Magnitude = magnitiude,
                Score = score,
            };

            // Make a single prediction on the sample data and print results
            var predictionResultVolume = predictionFunctionVolume.Predict(sampleDataVolume);
            var predictionResultHigh = predictionFunctionHigh.Predict(sampleDataHigh);
            var predictionResultLow = predictionFunctionLow.Predict(sampleDataLow);

            Console.WriteLine("Using model to make single prediction -- Comparing actual with predicted from sample data...\n\n");
            Console.WriteLine($"CompanyID: {sampleDataVolume.CompanyID}");
            Console.WriteLine($"Magnitude: {sampleDataVolume.Magnitude}");
            Console.WriteLine($"Score: {sampleDataVolume.Score}");
            Console.WriteLine($"\n\nPredicted Volume: {predictionResultVolume.Score}\n\n");
            Console.WriteLine($"\n\nPredicted High: {predictionResultHigh.Score}\n\n");
            Console.WriteLine($"\n\nPredicted Low: {predictionResultLow.Score}\n\n");
            Console.WriteLine("=============== End of process, hit any key to finish ===============");
            Console.ReadKey();
        }
    }
}
