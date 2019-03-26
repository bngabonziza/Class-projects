package edu.asu.cse535.group14.ecgproject;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.TextView;

import com.jjoe64.graphview.DefaultLabelFormatter;
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.DataPointInterface;
import com.jjoe64.graphview.series.LineGraphSeries;
import com.jjoe64.graphview.series.PointsGraphSeries;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.URL;


public class MainActivity extends AppCompatActivity
{

    SeekBar TimeSeek = null;
    Button BtnDownCSV = null;
    GraphView GraphECG, GraphHR1, GraphHR2 = null;
    TextView TxtSeek = null;

    int TimeIndex = 0;
    int BCMarker = 0;
    private LineGraphSeries seriesE, seriesK, seriesHR1, seriesHR1Pred;
    private PointsGraphSeries seriesR, seriesBC1;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        Common.Context = getApplicationContext();
        super.onCreate(savedInstanceState);

        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler()
        {
            @Override
            public void uncaughtException(Thread paramThread, Throwable e)
            {
                Log.e("CSE535", "exception", e);
            }
        });

        setContentView(R.layout.activity_main);

        Common.InitCSVFile();

        TxtSeek = (TextView)findViewById(R.id.TxtSeek);
        BtnDownCSV = (Button)findViewById(R.id.BtnDownCSV);
        TimeSeek = (SeekBar)findViewById(R.id.TimeSeek);
        GraphECG = (GraphView)findViewById(R.id.GraphECG);
        GraphHR1 = (GraphView)findViewById(R.id.GraphHR1);
        GraphHR2 = (GraphView)findViewById(R.id.GraphHR2);

        InitECGGraph();
        InitHRGraph1();
        InitHRGraph2();

        TxtSeek.setVisibility(View.INVISIBLE);
        TimeSeek.setVisibility(View.INVISIBLE);
        TxtSeek.setText("0");
        TimeSeek.setMax(460);

        TimeSeek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener()
        {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // updated continuously as the user slides the thumb
                try{TxtSeek.setText("Time Index: " + String.valueOf(progress));}
                catch (Exception e){}

            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
                // called when the user first touches the SeekBar
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                // called after the user finishes moving the SeekBar
                //T1.setText(String.format("%d", seekBar.getProgress()));
                TimeIndex = seekBar.getProgress();
                if (TimeIndex <= 0) TimeIndex = 10;
                if (TimeIndex >= 470) TimeIndex = 460;
                Log.e("CSE535", "TimeSeeker changed to " + TimeIndex);
                ShowECG();
            }
        });

        Log.e("CSE535", "Ready....");
    }

    public void BtnDownCSV_Click(View view)
    {
        BtnDownCSV.setVisibility(View.INVISIBLE);
        EnableControls(false);

        (new CSVLoadAsync()).execute(0);
        //(new CSVDownloadAsync()).execute(Common.CSV_FILE);
    }

    public void ShowECG()
    {

        try
        {
            Log.e("CSE535", "Getting Sublist...");
            Common.Data = ECG.GetSubList(TimeIndex, Common.MinsToLoad);
            Log.e("CSE535", "SubList done. Length=" + Common.Data.size());

            ///Common.Data = ECG.SmoothNoise(Common.Data);
            //Log.e("CSE535", "Smoothing done");

            //Common.Data = ECG.DetectPeaks(Common.Data);
            //Log.e("CSE535", "Peak detection done");

            //Common.Data = ECG.DeclusterPeaks(Common.Data);
            //Log.e("CSE535", "Declustering done");

            Log.e("CSE535", "Getting Heart Rate...");
            Common.HR1 = ECG.GetHeartRate(Common.Data, 60);

            Log.e("CSE535", "Getting ARIMA Prediction...");
            Common.HR1Pred = ECG.PredictHeartRate(Common.HR1, Common.ForecastSize, Common.ForecastLag);

            DrawECG();
            DrawHeartRate1();
        }
        catch (Exception e)
        {
            //Common.ShowMessage("Download failed: " + e.getMessage());
            Log.e("CSE535", "exception", e);
        }



    }

    private void InitECGGraph()
    {

        //Init the graph with a single point at 0,0
        GraphECG.setTitle("ECG with Kalman Smoothing and R-Peaks");

        seriesE = new LineGraphSeries<>();
        seriesK = new LineGraphSeries<>();
        seriesR = new PointsGraphSeries<>();

        GraphECG.getGridLabelRenderer().setHorizontalAxisTitle("Time (ms)");
        GraphECG.getGridLabelRenderer().setVerticalAxisTitle("Potential (uV)");

        //GraphECG.getViewport().setXAxisBoundsManual(true);
        //GraphECG.getViewport().setMinX(0);
        //GraphECG.getViewport().setMaxX(60);

        //GraphECG.getViewport().setYAxisBoundsManual(true);
        //GraphECG.getViewport().setMinY(-10);
        //GraphECG.getViewport().setMaxY(10);

        seriesE.setColor(Color.parseColor("blue"));  //X = Red
        seriesK.setColor(Color.parseColor("green"));  //Y = Green
        seriesR.setColor(Color.parseColor("red"));  //Z = Blue

        seriesE.setAnimated(false);
        seriesK.setAnimated(false);

        seriesE.setThickness(5);
        seriesK.setThickness(10);

        seriesR.setCustomShape(new PointsGraphSeries.CustomShape() {
            @Override
            public void draw(Canvas canvas, Paint paint, float x, float y, DataPointInterface dataPoint)
            {
                if (dataPoint.getY() != 0.0)
                {
                    paint.setStrokeWidth(5);
                    canvas.drawLine(x-20, y-20, x+20, y+20, paint);
                    canvas.drawLine(x+20, y-20, x-20, y+20, paint);

                }
            }
        });

        GraphECG.addSeries(seriesE);
        GraphECG.addSeries(seriesK);
        GraphECG.addSeries(seriesR);

        GraphECG.getGridLabelRenderer().setHorizontalLabelsVisible(false);
        //seriesR.setDrawAsPath(false);
        //seriesR.setDrawDataPoints(true);
        //seriesR.setDataPointsRadius(10);
        //seriesR.setThickness(8);

        GraphECG.getGridLabelRenderer().setLabelFormatter(new DefaultLabelFormatter()
        {
            @Override
            public String formatLabel(double value, boolean isValueX)
            {
                int v = (int) Math.round(value);
                return Integer.toString(v);
            }
        });

        ClearECGGraph();
    }

    private void InitHRGraph1()
    {

        //Init the graph with a single point at 0,0
        GraphHR1.setTitle("Heart Rate and Prediction with ARIMA");

        seriesHR1 = new LineGraphSeries<>();
        seriesHR1Pred = new LineGraphSeries<>();
        seriesBC1= new PointsGraphSeries<>();

        GraphHR1.getGridLabelRenderer().setHorizontalAxisTitle("Minutes");
        GraphHR1.getGridLabelRenderer().setVerticalAxisTitle("Beats");

        GraphHR1.getViewport().setXAxisBoundsManual(true);
        GraphHR1.getViewport().setMinX(0);
        GraphHR1.getViewport().setMaxX(60);

        GraphHR1.getViewport().setYAxisBoundsManual(true);
        GraphHR1.getViewport().setMinY(40);
        GraphHR1.getViewport().setMaxY(150);

        seriesHR1.setColor(Color.rgb(0, 255, 0));  //Y = Green
        seriesHR1Pred.setColor(Color.rgb(255, 0, 0));  //X = Red
        seriesBC1.setColor(Color.rgb(255, 255, 255));//White or invisible

        seriesHR1.setAnimated(false);
        seriesHR1Pred.setAnimated(false);

        seriesBC1.setSize(0);
        seriesBC1.setCustomShape(new PointsGraphSeries.CustomShape() {
            @Override
            public void draw(Canvas canvas, Paint paint, float x, float y, DataPointInterface dataPoint)
            {
                int hr = (int)dataPoint.getY();

                if ((hr <= Common.BradyCardia))
                {
                    paint.setColor(Color.rgb(0, 0, 255));
                }

                if ((hr <= Common.BradyCardia) && (BCMarker == 0))
                {
                    BCMarker++;
                    paint.setColor(Color.rgb(0, 0, 255));
                    paint.setStrokeWidth(10);
                    canvas.drawLine(x-20, y-20, x+20, y+20, paint);
                    canvas.drawLine(x+20, y-20, x-20, y+20, paint);

                    Log.e("CSE535", "****** BRADY CARDIA *****");
                }
            }
        });


        GraphHR1.addSeries(seriesHR1);
        GraphHR1.addSeries(seriesHR1Pred);
        GraphHR1.addSeries(seriesBC1);

        GraphHR1.getGridLabelRenderer().setLabelFormatter(new DefaultLabelFormatter()
        {
            @Override
            public String formatLabel(double value, boolean isValueX)
            {
                int v = (int) Math.round(value);
                return Integer.toString(v);
            }
        });

        ClearGraphHR1();
    }

    private void ClearGraphHR1()
    {
        BCMarker = 0;

        seriesHR1.resetData(new DataPoint[] {});
        seriesHR1Pred.resetData(new DataPoint[] {});
        seriesBC1.resetData(new DataPoint[] {});
        //seriesE.appendData(new DataPoint(0, 0), false, 60);
        //seriesK.appendData(new DataPoint(0, 0), false, 60);
        //seriesR.appendData(new DataPoint(0, 0), false, 60);
        GraphHR1.refreshDrawableState();
    }

    private void ClearGraphHR2()
    {
        BCMarker = 0;

        //seriesHR2.resetData(new DataPoint[] {});
        //seriesHR2Pred.resetData(new DataPoint[] {});
        //seriesBC2.resetData(new DataPoint[] {});
        //seriesE.appendData(new DataPoint(0, 0), false, 60);
        //seriesK.appendData(new DataPoint(0, 0), false, 60);
        //seriesR.appendData(new DataPoint(0, 0), false, 60);
        GraphHR2.refreshDrawableState();
    }

    private void InitHRGraph2()
    {

        //Init the graph with a single point at 0,0
        GraphHR2.setTitle("Heart Rate and Prediction with RNN");

        //seriesHR1 = new LineGraphSeries<>();
        //seriesHR1Pred = new LineGraphSeries<>();
        //seriesBC1= new PointsGraphSeries<>();

        GraphHR2.getGridLabelRenderer().setHorizontalAxisTitle("Minutes");
        GraphHR2.getGridLabelRenderer().setVerticalAxisTitle("Beats");

        GraphHR2.getViewport().setXAxisBoundsManual(true);
        GraphHR2.getViewport().setMinX(0);
        GraphHR2.getViewport().setMaxX(60);

        GraphHR2.getViewport().setYAxisBoundsManual(true);
        GraphHR2.getViewport().setMinY(40);
        GraphHR2.getViewport().setMaxY(150);

        //seriesHR1.setColor(Color.rgb(0, 255, 0));  //Y = Green
        //seriesHR1Pred.setColor(Color.rgb(255, 0, 0));  //X = Red
        //seriesBC1.setColor(Color.rgb(255, 255, 255));//White or invisible

        //seriesHR2.setAnimated(false);
        //seriesHR2Pred.setAnimated(false);

        /*
        seriesBC1.setSize(0);
        seriesBC1.setCustomShape(new PointsGraphSeries.CustomShape() {
            @Override
            public void draw(Canvas canvas, Paint paint, float x, float y, DataPointInterface dataPoint)
            {
                int hr = (int)dataPoint.getY();

                if ((hr <= 60) && (BCMarker == 0))
                {
                    BCMarker++;
                    paint.setColor(Color.rgb(0, 0, 255));
                    paint.setStrokeWidth(10);
                    canvas.drawLine(x-20, y-20, x+20, y+20, paint);
                    canvas.drawLine(x+20, y-20, x-20, y+20, paint);

                    Log.e("CSE535", "****** BRADY CARDIA *****");
                }
            }
        });
        */

        //GraphHR2.addSeries(seriesHR2);
        //GraphHR2.addSeries(seriesHR2Pred);
        //GraphHR2.addSeries(seriesBC2);

        GraphHR2.getGridLabelRenderer().setLabelFormatter(new DefaultLabelFormatter()
        {
            @Override
            public String formatLabel(double value, boolean isValueX)
            {
                int v = (int) Math.round(value);
                return Integer.toString(v);
            }
        });

        ClearGraphHR2();
    }

    private void ClearECGGraph()
    {
        seriesE.resetData(new DataPoint[] {});
        seriesK.resetData(new DataPoint[] {});
        seriesR.resetData(new DataPoint[] {});

        //seriesE.appendData(new DataPoint(0, 0), false, 60);
        //seriesK.appendData(new DataPoint(0, 0), false, 60);
        //seriesR.appendData(new DataPoint(0, 0), false, 60);
        GraphECG.refreshDrawableState();
    }

    private void DrawHeartRate1()
    {
        ClearGraphHR1();

        double hr = 0.0;
        int j = 0;
        int k = 0;

        for (int i = 0; i < Common.HR1.size(); i++)
        {

            hr = Common.HR1.get(i);

            seriesHR1.appendData(new DataPoint(k, hr), false, 30);
            k++;
        }

        k = k-1;
        seriesHR1Pred.appendData(new DataPoint(k, hr), false, 30);

        for (int i = 0; i < Common.HR1Pred.size(); i++)
        {
            hr = Common.HR1Pred.get(i);
            seriesHR1Pred.appendData(new DataPoint(k, hr), false, 30);
            seriesBC1.appendData(new DataPoint(k, hr), false, 30);
            k++;
        }

        GraphHR1.refreshDrawableState();
    }

    private void DrawECG()
    {
        ECG E;
        Double PV = 0.0;
        int Start, End, MaxPoints;

        Log.e("CSE535", "DrawECG");

        MaxPoints = 1000;
        End = Common.Data.size();
        Start = End - MaxPoints;

        ClearECGGraph();

        for (int i = Start; i < End; i++)
        {
            E = Common.Data.get(i);
            PV = 0.0;

            if (E.Peak)
            {
                PV = E.Signal * 1.05;
            }

            seriesE.appendData(new DataPoint(i, E.Signal), false, MaxPoints);
            seriesK.appendData(new DataPoint(i, E.SmoothSignal), false, MaxPoints);
            seriesR.appendData(new DataPoint(i, PV), false, MaxPoints);
        }

        GraphECG.refreshDrawableState();
    }


    private void EnableControls(boolean Enabled)
    {
        BtnDownCSV.setEnabled(Enabled);
    }

    public class CSVLoadAsync extends AsyncTask<Integer, Integer, Integer>
    {
        @Override
        protected Integer doInBackground(Integer... params)
        {
            try
            {
                //(new CSVDownloadAsync()).execute(Common.CSV_FILE);

                Log.e("CSE535", "Loading All CSV data...");
                Common.AllData = ECG.GetFinalData();
                Log.e("CSE535", "All data loaded.  Length = " + Common.AllData.size());

                return 1;
            }
            catch (Exception e)
            {
                //Common.ShowMessage("Download failed: " + e.getMessage());
                Log.e("CSE535", "exception", e);
            }

            return 0;
        }

        @Override
        protected void onPostExecute(Integer Result)
        {
            if (Result == 0) return;

            TimeIndex = 10;
            TimeSeek.setProgress(TimeIndex);
            ShowECG();

            TxtSeek.setVisibility(View.VISIBLE);
            TimeSeek.setVisibility(View.VISIBLE);
            BtnDownCSV.setVisibility(View.INVISIBLE);
        }
    }

    public class CSVDownloadAsync extends AsyncTask<String, Void, Integer>
    {

        @Override
        protected Integer doInBackground(String... params)
        {

            try
            {
                long total = 0;
                String DestinationFile = params[0];
                URL u = new URL(Common.SERVER_URL + Common.ECG_FILE);
                InputStream is = u.openStream();

                DataInputStream dis = new DataInputStream(is);

                byte[] buffer = new byte[1024];
                int length;

                FileOutputStream fos = new FileOutputStream(new File(DestinationFile));
                while ((length = dis.read(buffer))>0)
                {
                    total = total + length;
                    fos.write(buffer, 0, length);
                    Log.e("CSE535", "Downloaed: " + total);
                }

                BtnDownCSV.setTag(String.format("%d", total));

                fos.close();
                dis.close();
                is.close();

                //return size as success for the postexecute function
                return 1;
            }
            catch (Exception e)
            {
                //Common.ShowMessage("Download failed: " + e.getMessage());
                Log.e("CSE535", "exception", e);
            }


            return 0;

        }


        @Override
        protected void onPostExecute(Integer Size)
        {
            if (Size == 0)
            {
                Common.ShowMessage("Download has failed.");
                return;
            }

            EnableControls(true);
            Common.ShowMessage("ECG data has been downloaded.");
            Log.e("CSE535","ECG data has been downloaded.");
        }
    }
}
