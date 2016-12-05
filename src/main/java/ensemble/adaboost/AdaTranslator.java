
package ensemble.adaboost;

import org.jblas.MatrixFunctions;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;
import tree.TreeTranslator;
import org.jblas.DoubleMatrix;

import java.io.*;
import java.util.ArrayList;

public class AdaTranslator {

    private TreeTranslator[] _estimators = null;
    private String _algorithm = null;
    private double[] _estimator_weights = null;
    private int _n_estimators;
    private double _np_eps;

    public AdaTranslator(String directory) {
        /* header */
        read_header(directory + "/" + "header");
        String curr_file = null;
        int i = 0;
//        System.out.println(_n_estimators);
        for(i=0; i < _n_estimators; i++) {
            curr_file = directory + "/" + "estimator_" + Integer.toString(i);
//            System.out.println("estimator:");
//            System.out.println(curr_file);
//            System.out.println(curr_file);
            _estimators[i] = new TreeTranslator(curr_file);
        }
    }

    public DoubleMatrix predict_proba(ArrayList<Double> x) {
        DoubleMatrix res = null;
        if (_algorithm.equals("SAMME.R")) {
            res = _samme_proba(_estimators[0], x, 0);
//            System.out.println(res.toString() + ',');
            for (int i=1; i<_n_estimators; ++i) {
//                System.out.println(i);
                DoubleMatrix tmp = _samme_proba(_estimators[i], x, i);
//                System.out.println(tmp.toString()+',');
                res.addi(tmp);
            }
        } else {
            throw new NotImplementedException();
        }
        return res;
    }

    private DoubleMatrix _samme_proba(TreeTranslator estimator, ArrayList<Double> x, int i) {
        int n_classes = estimator.get_n_classes();
        DoubleMatrix p = estimator.predict_proba(x, i);
//        if (i==1256) {
//            System.out.println(i);
//            System.out.println(p);
//        }
        DoubleMatrix eps_pos_mat = p.lt(_np_eps);
        p.put(eps_pos_mat, _np_eps);
        p = MatrixFunctions.log(p);
        DoubleMatrix row_sum = p.rowSums();
        row_sum.muli(1.0/n_classes);
        p.subiColumnVector(row_sum);
        p.muli(n_classes - 1);
        return p;
    }

    private void read_header(String fpath) {
        File fd = new File(fpath);
        BufferedReader reader = null;
        String line = null;
        try {
            reader = new BufferedReader(new InputStreamReader(new FileInputStream(fd), "UTF-8"), 512);
            while ((line = get_non_empty_line(reader))!=null) {
                if (_estimators ==null && line.equals("# estimator_weights")) {
                    line = get_non_empty_line(reader);
                    String[] tmp = line.split(",");
                    _n_estimators = tmp.length;
                    init_param();
                    for (int i=0;  i<_n_estimators; ++i) {
                        _estimator_weights[i] = Double.parseDouble(tmp[i]);
                    }
                } else if (_algorithm == null && line.equals("# algorithm")) {
                    _algorithm = get_non_empty_line(reader);
                    System.out.println(_algorithm);
                } else if (line.equals("# np_eps")) {
                    line = get_non_empty_line(reader);
                    _np_eps = Double.parseDouble(line);
                    System.out.println(_np_eps);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (reader!=null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private void init_param() {
        _estimators = new TreeTranslator[_n_estimators];
        _estimator_weights = new double[_n_estimators];
    }

    private String get_non_empty_line(BufferedReader reader) throws IOException {
        String line;
        while ((line = reader.readLine())!=null) {
            /* 跳过空白行 */
            line = line.trim();
            if (line.isEmpty()) {
                continue;
            } else {
                break;
            }
        }
        //System.out.println(line);
        return line;
    }

    public static void main(String[] args) throws java.lang.Exception {
        AdaTranslator inst = new AdaTranslator("/folder path for adaboost models");
        ArrayList<Double> x = new ArrayList<Double>(200000);
        String data_path = new String("x.txt");
        File fd = null;
        BufferedReader reader = null;
        try {
            fd = new File(data_path);
            reader = new BufferedReader(new InputStreamReader(new FileInputStream(fd), "UTF-8"), 512);
            String line = inst.get_non_empty_line(reader);
            String[] tmp = line.split(",");
            for (int i=0;  i<tmp.length; ++i) {
                x.add(Double.parseDouble(tmp[i]));
            }
            long startTime = System.currentTimeMillis();//获取当前时间
            DoubleMatrix p = null;
            for (int i=0; i<1000; ++i) {
               p = inst.predict_proba(x);
            }
            long endTime = System.currentTimeMillis();
            System.out.println("程序运行时间："+(endTime-startTime)/1000.0+"ms");
            System.out.println(p);
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (reader!=null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}