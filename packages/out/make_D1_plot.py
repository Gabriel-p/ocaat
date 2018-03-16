
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from os.path import join
import add_version_plot
import mp_best_fit1_GA
import mp_best_fit1_emcee
import prep_plots


def main(
        npd, pd, isoch_fit_params, fit_params_r, fit_errors_r, **kwargs):
    '''
    Make D1 block plots.
    '''
    if 'D1' in pd['flag_make_plot'] and pd['bf_flag']:
        fig = plt.figure(figsize=(30, 30))
        gs = gridspec.GridSpec(12, 12)
        add_version_plot.main(y_fix=.999)

        min_max_p = prep_plots.param_ranges(pd['fundam_params'])
        # DEPRECATED (DELETE)
        # # Get special axis ticks for metallicity.
        # xp_min, xp_max = min_max_p[0]
        # # The max number of characters in the axis '30', is HARD-CODED.
        # # Add values to the end of this list.
        # min_max_p.append(prep_plots.BestTick(xp_min, xp_max, 30))

        # Extract outside of 'if' block so it works when the 'brute force'
        # algorithm was used
        model_done = isoch_fit_params[-1]

        # Best fitting process plots.
        if pd['best_fit_algor'] == 'genet':
            lkl_old, new_bs_indx = isoch_fit_params[1:3]
            l_min_max = prep_plots.likl_y_range(pd['best_fit_algor'], lkl_old)
            args = [
                # pl_lkl: Likelihood evolution for the GA.
                gs, l_min_max, lkl_old, model_done, new_bs_indx,
                pd['N_pop'], pd['N_gen'], pd['fit_diff'], pd['cross_prob'],
                pd['cross_sel'], pd['mut_prob'], pd['N_el'], pd['N_ei'],
                pd['N_es'], pd['N_bootstrap']
            ]
            mp_best_fit1_GA.plot(0, *args)

        if pd['best_fit_algor'] in ['brute', 'genet']:
            arglist = [
                # pl_2_param_dens: Param vs param solutions scatter map.
                [gs, 'age-metal', min_max_p, fit_params_r, fit_errors_r,
                 model_done],
                [gs, 'dist-ext', min_max_p, fit_params_r, fit_errors_r,
                 model_done],
                [gs, 'ext-age', min_max_p, fit_params_r, fit_errors_r,
                 model_done],
                [gs, 'mass-binar', min_max_p, fit_params_r, fit_errors_r,
                 model_done],
                # pl_lkl_scatt: Parameter likelihood density plot.
                [gs, '$z$', min_max_p, fit_params_r, fit_errors_r, model_done],
                [gs, '$log(age)$', min_max_p, fit_params_r, fit_errors_r,
                 model_done],
                [gs, '$E_{{(B-V)}}$', min_max_p, fit_params_r, fit_errors_r,
                 model_done],
                [gs, '$(m-M)_o$', min_max_p, fit_params_r, fit_errors_r,
                 model_done],
                [gs, '$M\,(M_{{\odot}})$', min_max_p, fit_params_r,
                 fit_errors_r, model_done],
                [gs, '$b_{{frac}}$', min_max_p, fit_params_r, fit_errors_r,
                 model_done]
            ]
            for n, args in enumerate(arglist, 1):
                mp_best_fit1_GA.plot(n, *args)

        if pd['best_fit_algor'] == 'emcee':
            pars_chains, m_accpt_fr, varIdxs = isoch_fit_params[1:4]
            # Limits for the 2-dens plots.
            min_max_p2 = prep_plots.p2_ranges(
                min_max_p, varIdxs, model_done, pd['nwalkers'], pd['nsteps'])

            # pl_2_param_dens: Param vs param density map.
            for p2 in [
                    'metal-age', 'metal-ext', 'metal-dist', 'metal-mass',
                    'metal-binar', 'age-ext', 'age-dist', 'age-mass',
                    'age-binar', 'ext-dist', 'ext-mass', 'ext-binar',
                    'dist-mass', 'dist-binar', 'mass-binar']:
                args = [p2, gs, min_max_p2, fit_params_r, fit_errors_r,
                        varIdxs, model_done]
                mp_best_fit1_emcee.plot(0, *args)

            # pl_param_pf: Parameters probability functions.
            for p in ['metal', 'age', 'ext', 'dist', 'mass', 'binar']:
                args = [p, gs, min_max_p2, fit_params_r, fit_errors_r,
                        varIdxs, model_done]
                mp_best_fit1_emcee.plot(1, *args)

            # pl_pdf_half: Parameters half of pdfs.
            for p in ['metal', 'age', 'ext', 'dist', 'mass', 'binar']:
                args = [p, gs, min_max_p, varIdxs, model_done]
                mp_best_fit1_emcee.plot(2, *args)

            # pl_param_chain: Parameters sampler chains.
            for p in ['metal', 'age', 'ext', 'dist', 'mass', 'binar']:
                args = [
                    p, gs, min_max_p, fit_params_r, pd['nwalkers'],
                    pd['nsteps'], pd['nburn'], m_accpt_fr, varIdxs,
                    pars_chains]
                mp_best_fit1_emcee.plot(3, *args)

        # Generate output file.
        fig.tight_layout()
        plt.savefig(
            join(npd['output_subdir'], str(npd['clust_name']) +
                 '_D1.' + pd['plot_frmt']), dpi=pd['plot_dpi'],
            bbox_inches='tight')
        # Close to release memory.
        plt.clf()
        plt.close("all")

        print("<<Plots for D1 block created>>")
    else:
        print("<<Skip D1 block plot>>")
