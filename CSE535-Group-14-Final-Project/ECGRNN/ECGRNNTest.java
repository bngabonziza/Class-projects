
import org.datavec.api.records.reader.SequenceRecordReader;
import org.datavec.api.records.reader.impl.csv.CSVSequenceRecordReader;
import org.datavec.api.split.NumberedFileInputSplit;
import org.datavec.api.util.ClassPathResource;
import org.deeplearning4j.datasets.datavec.SequenceRecordReaderDataSetIterator;
import org.deeplearning4j.eval.RegressionEvaluation;
import org.deeplearning4j.nn.api.OptimizationAlgorithm;
import org.deeplearning4j.nn.conf.GradientNormalization;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.conf.Updater;
import org.deeplearning4j.nn.conf.layers.GravesLSTM;
import org.deeplearning4j.nn.conf.layers.RnnOutputLayer;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.deeplearning4j.nn.weights.WeightInit;
import org.deeplearning4j.optimize.listeners.ScoreIterationListener;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.RefineryUtilities;
import org.nd4j.linalg.activations.Activation;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.dataset.api.iterator.DataSetIterator;
import org.nd4j.linalg.dataset.api.preprocessor.NormalizerMinMaxScaler;
import org.nd4j.linalg.learning.config.Nesterovs;
import org.nd4j.linalg.lossfunctions.LossFunctions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.swing.*;
import java.io.File;

public class ECGRNNTest
{

    private static final Logger LOGGER = LoggerFactory.getLogger(ECGRNNTest.class);

    public static void main(String[] args) throws Exception
    {
        //File baseDir = new ClassPathResource("/rnnRegression").getFile();
        int miniBatchSize = 32;
        double learningRate = 0.1;
        long seed = 1525314865089L;// System.currentTimeMillis();  //1525314865089

        // ----- Load the training data -----
        SequenceRecordReader trainReader = new CSVSequenceRecordReader(1, ",");
        trainReader.initialize(new NumberedFileInputSplit("C:\\Work\\ECG\\RNN\\Train_%d.csv", 0, 0));

        //For regression, numPossibleLabels is not used. Setting it to -1 here
        DataSetIterator trainIter = new SequenceRecordReaderDataSetIterator(trainReader, miniBatchSize, -1, 1, true);

        SequenceRecordReader testReader = new CSVSequenceRecordReader(1, ",");
        testReader.initialize(new NumberedFileInputSplit("C:\\Work\\ECG\\RNN\\Test_%d.csv", 0, 0));
        DataSetIterator testIter = new SequenceRecordReaderDataSetIterator(testReader, miniBatchSize, -1, 1, true);

        //Create data set from iterator here since we only have a single data set
        DataSet trainData = trainIter.next();
        DataSet testData = testIter.next();

        //Normalize data, including labels (fitLabel=true)
        NormalizerMinMaxScaler normalizer = new NormalizerMinMaxScaler(0, 1);
        normalizer.fitLabel(true);
        normalizer.fit(trainData);              //Collect training data statistics

        normalizer.transform(trainData);
        normalizer.transform(testData);

        // ----- Configure the network -----
        NeuralNetConfiguration.Builder builder = new NeuralNetConfiguration.Builder();
        builder.seed(seed);
        builder.optimizationAlgo(OptimizationAlgorithm.STOCHASTIC_GRADIENT_DESCENT);
        builder.gradientNormalization(GradientNormalization.ClipL2PerLayer);
        builder.gradientNormalizationThreshold(0.1);
        builder.updater(new Nesterovs(learningRate, 0.3));
        NeuralNetConfiguration.ListBuilder listBuilder = builder.list();


        int numInput = 1;
        int numOutputs = 5;
        int nLayers = 2;
        int LayerIndex = 0;

        listBuilder.layer(LayerIndex, new GravesLSTM.Builder().activation(Activation.TANH).nIn(numInput).nOut(numOutputs).build());


        for (int h = 1; h <= nLayers; h++)
        {
            LayerIndex++;
            listBuilder.layer(LayerIndex, new GravesLSTM.Builder().activation(Activation.TANH).nIn(numOutputs).nOut(numOutputs).build());
        }

        LayerIndex++;
        listBuilder.layer(LayerIndex, new RnnOutputLayer.Builder(LossFunctions.LossFunction.MSE).activation(Activation.IDENTITY).nIn(numOutputs).nOut(numInput).build());

        MultiLayerConfiguration conf = listBuilder.build();
        MultiLayerNetwork net = new MultiLayerNetwork(conf);
        net.init();

        net.setListeners(new ScoreIterationListener(20));

        // ----- Train the network, evaluating the test set performance at each epoch -----
        int nEpochs = 30;

        for (int i = 0; i < nEpochs; i++) {
            net.fit(trainData);
            LOGGER.info("Epoch " + i + " complete. Time series evaluation:");

            //Run regression evaluation on our single column input
            RegressionEvaluation evaluation = new RegressionEvaluation(1);
            INDArray features = testData.getFeatureMatrix();

            INDArray lables = testData.getLabels();
            INDArray predicted = net.output(features, false);

            evaluation.evalTimeSeries(lables, predicted);

            //Just do sout here since the logger will shift the shift the columns of the stats
            System.out.println(evaluation.stats());
        }

        //Init rrnTimeStemp with train data and predict test data
        net.rnnTimeStep(trainData.getFeatureMatrix());
        INDArray predicted = net.rnnTimeStep(testData.getFeatureMatrix());

        //Revert data back to original values for plotting
        normalizer.revert(trainData);
        normalizer.revert(testData);
        normalizer.revertLabels(predicted);

        INDArray trainFeatures = trainData.getFeatures();
        INDArray testFeatures = testData.getFeatures();
        //Create plot with out data
        XYSeriesCollection c = new XYSeriesCollection();
        createSeries(c, trainFeatures, 0, "Train Data");
        createSeries(c, testFeatures, 30, "Test Data");
        createSeries(c, predicted, 31, "Predictedion");

        plotDataset(c);

        System.out.println("seed = " + seed);

        for (int i=0; i < predicted.length(); i++)
        {
            System.out.println(predicted.getDouble(i) + "\t" + trainFeatures.getDouble(i));
        }
    }

    private static  void createSeries(XYSeriesCollection seriesCollection, INDArray data, int offset, String name) {
        int nRows = data.shape()[2];
        XYSeries series = new XYSeries(name);
        for (int i = 0; i < nRows; i++) {
            series.add(i + offset, data.getDouble(i));
        }
        seriesCollection.addSeries(series);
    }


    private static  void plotDataset(XYSeriesCollection c) {

        String title = "";
        String xAxisLabel = "Time (min)";
        String yAxisLabel = "Heart Rate";
        PlotOrientation orientation = PlotOrientation.VERTICAL;
        boolean legend = true;
        boolean tooltips = false;
        boolean urls = false;
        JFreeChart chart = ChartFactory.createXYLineChart(title, xAxisLabel, yAxisLabel, c, orientation, legend, tooltips, urls);

        // get a reference to the plot for further customisation...
        final XYPlot plot = chart.getXYPlot();

        // Auto zoom to fit time series in initial window
        final NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        rangeAxis.setAutoRange(true);

        JPanel panel = new ChartPanel(chart);

        JFrame f = new JFrame();
        f.add(panel);
        f.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        f.pack();
        f.setTitle("Training Data");

        RefineryUtilities.centerFrameOnScreen(f);
        f.setVisible(true);
    }

}
