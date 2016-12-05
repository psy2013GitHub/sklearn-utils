
package tree;

import java.io.*;
import java.util.ArrayList;

import java.lang.String;
import org.jblas.DoubleMatrix;
import org.jblas.ranges.IndicesRange;
import org.jblas.ranges.IntervalRange;


/*
*
# n_outputs:
1
# classes:
0,1
# lChilds:
1,2,3,4,-1,-1,7,-1,-1,10,11,-1,-1,-1,15,16,17,-1,-1,-1,21,22,-1,-1,-1
# rChilds:
14,9,6,5,-1,-1,8,-1,-1,13,12,-1,-1,-1,20,19,18,-1,-1,-1,24,23,-1,-1,-1
# feature:
106,11214,12504,5753,-2,-2,2661,-2,-2,10882,13324,-2,-2,-2,490,130,11214,-2,-2,-2,1862,6497,-2,-2,-2
# threshold:
0.5,0.5,0.5,0.5,-2.0,-2.0,0.5,-2.0,-2.0,0.5,0.5,-2.0,-2.0,-2.0,0.5,0.5,0.5,-2.0,-2.0,-2.0,0.5,0.5,-2.0,-2.0,-2.0
# value:
*
*
*
* */


public class TreeTranslator {

    private int[] classes; // 类别个数
    private int n_classes;
    private int[] lChilds;
    private int[] rChilds;
    private int[] feature;
    private double[] threshold;
    private ArrayList value;
    private int n_outputs; // 输出
    private int n_nodes; // 节点个数
    private int TREE_LEAF;
    private int TREE_UNDEFINED;

    public TreeTranslator(String fpath) {
        String[] tmp = null;
        String line;
        int value_row = -1; // 读到第几行value
        int node_idx = 0;
        int output_idx = 0;
        File fd = null;
        BufferedReader reader = null;
        try {
            fd = new File(fpath);
            reader = new BufferedReader(new InputStreamReader(new FileInputStream(fd), "UTF-8"), 512);

            if ((line=get_non_empty_line(reader))!=null) {

                /* header */
                if (!line.equals("# n_nodes")) {
                    throw new IOException("fuck");
                }
                line = get_non_empty_line(reader);
                n_nodes = Integer.parseInt(line);
                line = get_non_empty_line(reader);

                if (!line.equals("# n_outputs")) {
                    throw new IOException("fuck");
                }
                line = get_non_empty_line(reader);
                n_outputs = Integer.parseInt(line);
                line = get_non_empty_line(reader);

                if (!line.equals("# n_classes")) {
                    throw new IOException("fuck");
                }
                line = get_non_empty_line(reader);
                n_classes = Integer.parseInt(line);

//                if (line.equals("# classes")==false) {
//                    throw new IOException("fuck");
//                }
//                line = reader.readLine();
//                tmp = line.split(",");
//                for (int i=0;  i<tmp.length; ++i) {
//                    classes[i] = Integer.parseInt(tmp[i]);
//                }
//                if ((line = reader.readLine())==null) {
//                    break;
//                }

                /* 初始化 */
                classes = new int[n_classes];
                lChilds = new int[n_nodes];
                rChilds = new int[n_nodes];
                feature = new int[n_nodes];
                threshold = new double[n_nodes];
                value = new ArrayList(n_nodes);
                for (int i=0; i<n_nodes; ++i) {
                    value.add(new DoubleMatrix(n_outputs, n_classes));
                }

                /* body */
                while ((line=get_non_empty_line(reader))!=null) {
                    if (line.equals("# TREE_LEAF")) {
                        line = get_non_empty_line(reader);
                        TREE_LEAF = Integer.parseInt(line);
                    } else if (line.equals("# TREE_UNDEFINED")) {
                        line = get_non_empty_line(reader);
                        TREE_UNDEFINED = Integer.parseInt(line);
;
                    } else if (line.equals("# classes")) {
                        line = get_non_empty_line(reader);
                        tmp = line.split(",");
                        for (int i=0;  i<tmp.length; ++i) {
                            classes[i] = Integer.parseInt(tmp[i]);
                        }
                    } else if (line.equals("# lChilds")) {
                        line = get_non_empty_line(reader);
                        tmp = line.split(",");
                        for (int i=0;  i<tmp.length; ++i) {
                            lChilds[i] = Integer.parseInt(tmp[i]);
                        }
                    } else if (line.equals("# rChilds")) {
                        line = get_non_empty_line(reader);
                        tmp = line.split(",");
                        for (int i=0;  i<tmp.length; ++i) {
                            rChilds[i] = Integer.parseInt(tmp[i]);
                        }
                    } else if (line.equals("# feature")) {
                        line = get_non_empty_line(reader);
                        tmp = line.split(",");
                        for (int i=0;  i<tmp.length; ++i) {
                            feature[i] = Integer.parseInt(tmp[i]);
                        }
                    } else if (line.equals("# threshold")) {
                        line = get_non_empty_line(reader);
                        tmp = line.split(",");
                        for (int i=0;  i<tmp.length; ++i) {
                            threshold[i] = Double.parseDouble(tmp[i]);
                        }
                    }
                    else if (line.equals("# value")) {
                        while ((line=get_non_empty_line(reader))!=null) {
                            tmp = line.split(",");
                            value_row += 1;
                            node_idx = value_row / n_outputs;
                            output_idx = value_row % n_outputs;
                            if (tmp.length != n_classes) {
                                throw new IOException("fuxk");
                            }
                            for (int i=0;  i<tmp.length; ++i) {
//                                System.out.println("value_row:" + Integer.toString(value_row) + " node_idx:" + Integer.toString(node_idx) + " output_idx:" + Integer.toString(output_idx) + " i:" + Integer.toString(output_idx, i));
                                ((DoubleMatrix)value.get(node_idx)).put(output_idx, i, Double.parseDouble(tmp[i]));
                            }
                        }
                    }
                }
            }
//            System.out.println(value.toString());
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

    public DoubleMatrix predict_raw_proba(ArrayList<Double> x, int idx) {
        DoubleMatrix res=null;
        int i = 0;
        while (true) {
            int curr_feature = feature[i];
            double curr_thresh = threshold[i];
//            if (idx==1256) {
//                System.out.println(i);
//                System.out.println("curr_feature:");
//                System.out.println(curr_feature);
//                System.out.println("curr_thresh:");
//                System.out.println(curr_thresh);
//            }
            if (curr_feature == TREE_UNDEFINED || curr_thresh == TREE_UNDEFINED) {
                break;
            }
//            if (idx==1256) {
//                System.out.println("curr_x:");
//                System.out.println(x.get(curr_feature).toString());
//            }
            if (x.get(curr_feature) <= curr_thresh) {
                i = lChilds[i];
                if (i == TREE_LEAF) {
                    break;
                }
            }
            else {
                i = rChilds[i];
                if (i == TREE_LEAF) {
                    break;
                }
            }
        }
        res = (DoubleMatrix) value.get(i);
        return res;
    }

    public int get_n_classes() {
        return n_classes;
    }

    public DoubleMatrix predict_proba(ArrayList<Double> x, int idx) {
        DoubleMatrix normalizer; // 概率标准化因子
//        System.out.println("value:");
//        System.out.println(value);
        DoubleMatrix p = predict_raw_proba(x, idx);
//        System.out.println("raw_p:");
//        System.out.println(p.toString());
//        System.out.println(p.rows);
//        System.out.println(p.columns);
        IntervalRange all_row_idx = new IntervalRange(0, n_outputs);
//        System.out.println("all_row_idx:");
//        System.out.println(all_row_idx);
        IntervalRange col_idx = new IntervalRange(0, n_classes);
//        System.out.println("col_idx:");
//        System.out.println(col_idx);
        DoubleMatrix zero_mat;
        //IndicesRange zero_idx;
        if (n_outputs == 1) {
            p = p.get(all_row_idx, col_idx);
//            System.out.println("p:");
//            System.out.println(p.toString());
            normalizer = p.rowSums(); // fixme
//            System.out.println("normalizer:");
//            System.out.println(normalizer.toString());
            /* 获得零下标 */
            zero_mat = normalizer.not(); // Maps zero to 1.0 and all non-zero values to 0.0.
            normalizer.put(zero_mat, 1.0);
            p.diviColumnVector(normalizer);
            return p;
        } else {
//            all_proba = [];
//            for (int k=0; k<n_outputs; ++k) {
//                proba_k = p[:, k, :self.n_classes[k]];
//                normalizer = proba_k.sum(axis=1)[:, np.newaxis];
//                normalizer[normalizer == 0.0] = 1.0;
//                proba_k /= normalizer;
//                all_proba.append(proba_k);
//                return all_proba;
//            }
            ;
        }
        return p;
    }

    private String get_non_empty_line(BufferedReader reader) throws IOException {
        String line;
        while ((line = reader.readLine())!=null) {
            /* 跳过空白行 */
            line = line.trim();
            if (!line.isEmpty()) {
                break;
            }
        }
        //System.out.println(line);
        return line;
    }

    public static void main(String[] args) throws java.lang.Exception {
        TreeTranslator inst = new TreeTranslator("test.tree");
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
            for (int i=0; i<1500; ++i) {
                DoubleMatrix p = inst.predict_proba(x, 0);
            }
            long endTime = System.currentTimeMillis();
            System.out.println("程序运行时间："+(endTime-startTime)+"ms");
            System.out.println(inst.predict_proba(x, 0));
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