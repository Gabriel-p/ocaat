
import time
import gc  # Garbage collector.
#
from .inp import names_paths
from .inp import get_manual_strct
from .inp import get_data
# from .structure import trim_frame  # DEPRECATED
from .structure import histo_2d
from .structure import xy_density
from .structure import center
from .structure import radius
from .structure import field_density
from .structure import integMags
from .structure import cluster_area
from .structure import contamination_index
from .structure import king_profile
from .errors import err_accpt_rejct
from .structure import stars_in_out_cl_reg
from .structure import field_regions
from .errors import err_range_avrg
#
from .data_analysis import compl_err_funcs
from .data_analysis import luminosity
from .data_analysis import ad_field_vs_clust
from .data_analysis import members_number
#
from .decont_algors import decont_algors
from .decont_algors import members_N_compare
from .decont_algors import cl_region_clean
#
from .data_analysis import plx_analysis
from .data_analysis import pms_analysis
#
from .out import inparams_out
from .out import cluster_members_file
from .best_fit import best_fit_synth_cl
from .out import synth_cl_file
from .out import create_out_data_file
#
from .out import add_data_output
from .out import make_A1_plot
from .out import make_A2_plot
from .out import make_A3_plot
from .out import photComb
from .out import make_B1_plot
from .out import make_B2_plot
from .out import make_B3_plot
from .out import make_C1_plot
from .out import make_C2_plot
from .out import make_C3_plot
from .out import make_D1_plot
from .out import make_D2_plot
from .out import make_D3_plot


def main(cl_file, pd):
    """
    Call each function sequentially. Four dictionaries are passed around:

    pd : contains all the input parameters stored in 'params_input.dat'.

    npd : names and paths for the cluster and all the files generated.
    Generated by 'names_paths' and never modified.

    cld : read cluster data. Generated by 'get_data'

    clp : contains all the information about the cluster gathered by the
    functions applied. Modified constantly throughout the code.
    """

    # Start timing this loop.
    start = time.time()

    # File names (n) and paths (p) dictionary (d).
    npd = names_paths.main(cl_file, **pd)

    # Save params_input.dat file used.
    inparams_out.main(npd, **pd)

    # Get manual structural data and add to dictionary.
    pd = get_manual_strct.main(pd, **npd)

    # Cluster's data from file, as dictionary. Obtain both incomplete (ie: all
    # stars in data file) and complete (only those with full photometric data)
    # dictionaries.
    # Initiates cluster's parameters dictionary 'clp'.
    cld_i, cld_c, clp = get_data.main(npd, **pd)

    # DEPRECATED (at least for now, 08/05/18)
    # If Manual mode is set, display frame and ask if it should be trimmed.
    # cld = trim_frame.main(cld, **pd)

    # Obtain 2D coordinates histogram for the observed frame.
    clp = histo_2d.main(clp, **cld_i)

    # Gaussian filtered 2D x,y histograms.
    clp = xy_density.main(clp, cld_i, **pd)

    make_A1_plot.main(npd, cld_i, pd, **clp)
    if pd['stop_idx'] == 'A1':
        retFunc(npd['clust_name'], start)
        return

    # Cluster's center coordinates and errors.
    clp = center.main(cld_i, clp, **pd)

    # Field density value in stars/<area unit>.
    clp = field_density.main(clp, cld_i, **pd)

    # Integrated magnitude. For plotting purposes only.
    clp = integMags.main(clp, **cld_i)

    # Cluster radius
    clp = radius.main(cld_i, clp, **pd)

    # Uses the incomplete data.
    make_A2_plot.main(npd, cld_i, pd, **clp)
    if pd['stop_idx'] == 'A2':
        retFunc(npd['clust_name'], start)
        return

    # Cluster's area and total number of stars within the cluster region.
    clp = cluster_area.main(clp, **cld_i)

    # Contamination index.
    clp = contamination_index.main(clp, **cld_i)

    # King profiles based on the density profiles.
    clp = king_profile.main(clp, cld_i, **pd)

    # ^ All the functions above use the *photo incomplete* dataset 'cld_i'

    # These three functions are applied for both datasets since we need the
    # 'cl_region' and 'field_regions' parameters with *photo incomplete* data
    # to be used by the DA, and the parameters obtained with the
    # *photo complete* dataset for the rest of the functions.
    print("Processing complete dataset:")
    # Accept and reject stars based on their errors.
    clp = err_accpt_rejct.main('comp', cld_c, clp, **pd)

    # Stars in and out of cluster's radius.
    clp = stars_in_out_cl_reg.main('comp', clp)

    # Field regions around the cluster's center.
    clp = field_regions.main('comp', clp, **pd)

    # Only process incomplete data if the the input data is not equal. Else
    # just use the complete dataset.
    if clp['flag_data_eq']:
        clp['cl_region_i'], clp['flag_no_fl_regs_i'], clp['field_regions_i'], \
            clp['cl_region_rjct_i'], clp['field_regions_rjct_i'] =\
            clp['cl_region_c'], clp['flag_no_fl_regs_c'],\
            clp['field_regions_c'], clp['cl_region_rjct_c'],\
            clp['field_regions_rjct_c']
    else:
        print("Processing incomplete dataset:")
        clp = err_accpt_rejct.main('incomp', cld_i, clp, **pd)
        clp = stars_in_out_cl_reg.main('incomp', clp)
        clp = field_regions.main('incomp', clp, **pd)

    # This is what these three functions generate. The 'x' separates incomplete
    # (i) and complete (c) data.
    #
    # err_accpt_rejct -------> acpt_stars_x
    #       |        '-------> rjct_stars_x
    #       |
    #       v
    # stars_in_out_cl_reg ---> acpt_stars_x --> cl_region_x
    #       |            |                 '--> stars_out_x
    #       |            |
    #       |            '---> rjct_stars_x --> cl_region_rjct_x
    #       |                              '--> stars_out_rjct_x
    #       v
    # field_regions --> stars_out_x ----------> field_regions_x
    #              '--> stars_out_rjct_x -----> field_regions_rjct_x

    # Uses the incomplete 'cl_region' and 'field_regions' data.
    make_A3_plot.main(npd, cld_i, pd, **clp)
    if pd['stop_idx'] == 'A3':
        retFunc(npd['clust_name'], start)
        return

    # v The functions below use the *photom complete* dataset with the
    # exception of the 'compl_err_funcs()' function and the Bayesian DA. The
    # DA uses the *photo incomplete* dataset to assign MPs. After this, only
    # those stars in the *photo complete* dataset are kept and passed forward
    # to the fundamental parameters estimation process.

    # Obtain exponential fit for the errors.
    clp = err_range_avrg.main(clp)

    # Combined error rejection & completeness function.
    clp = compl_err_funcs.main(clp, cld_i, cld_c)

    # Helper function for plotting.
    clp = photComb.main(pd, clp)

    make_B1_plot.main(npd, cld_c, pd, **clp)
    if pd['stop_idx'] == 'B1':
        retFunc(npd['clust_name'], start)
        return

    # Luminosity function and completeness level for each magnitude bin.
    clp = luminosity.main(clp, **cld_c)

    # Approximate number of cluster's members.
    clp = members_number.main(clp)

    make_B2_plot.main(npd, cld_c, pd, **clp)
    if pd['stop_idx'] == 'B2':
        retFunc(npd['clust_name'], start)
        return

    clp = ad_field_vs_clust.main(clp, cld_c, **pd)

    make_B3_plot.main(npd, pd, **clp)
    if pd['stop_idx'] == 'B3':
        retFunc(npd['clust_name'], start)
        return

    # Apply decontamination algorithm.
    clp = decont_algors.main(clp, npd, **pd)

    # Obtain members parameter.
    clp = members_N_compare.main(clp)

    # Remove stars from the observed cluster according to a selected method.
    clp = cl_region_clean.main(clp, **pd)

    # Create data file with membership probabilities.
    cluster_members_file.main(clp, npd, **pd)

    make_C1_plot.main(npd, cld_c, pd, **clp)
    if pd['stop_idx'] == 'C1':
        retFunc(npd['clust_name'], start)
        return

    # Analyze parallax data if available.
    clp = plx_analysis.main(clp, **pd)

    # Analyze PMs data if available.
    clp = pms_analysis.main(clp, cld_i, **pd)

    make_C2_plot.main(npd, pd, **clp)
    if pd['stop_idx'] == 'C2':
        retFunc(npd['clust_name'], start)
        return
    make_C3_plot.main(npd, pd, cld_i, **clp)
    if pd['stop_idx'] == 'C3':
        retFunc(npd['clust_name'], start)
        return

    # Obtain best fitting parameters for cluster.
    clp = best_fit_synth_cl.main(npd, pd, clp)

    # If this mode was used, break out here.
    if pd['best_fit_algor'] == 'synth_gen':
        retFunc(npd['clust_name'], start)
        return

    # Create output synthetic cluster file if one was found
    clp = synth_cl_file.main(clp, npd, **pd)

    # Create template output data file in /output dir.
    create_out_data_file.main(npd)

    # Add cluster data output file
    add_data_output.main(npd, pd, **clp)

    # Convergence plots.
    make_D1_plot.main(npd, pd, **clp)
    if pd['stop_idx'] == 'D1':
        retFunc(npd['clust_name'], start)
        return
    # Corner plot.
    make_D2_plot.main(npd, pd, **clp)
    if pd['stop_idx'] == 'D2':
        retFunc(npd['clust_name'], start)
        return

    # Plot final best match found.
    make_D3_plot.main(npd, pd, **clp)
    retFunc(npd['clust_name'], start)


def retFunc(clname, start):
    elapsed = time.time() - start
    m, s = divmod(elapsed, 60)
    if m > 60:
        h, m = divmod(m, 60)
        t = "{:.0f}h {:.0f}m {:.0f}s".format(h, m, s)
    else:
        t = "{:.0f}m {:.0f}s".format(m, s)
    print("End of analysis for {} in {}\n".format(clname, t))

    # Force the Garbage Collector to release unreferenced memory.
    gc.collect()
