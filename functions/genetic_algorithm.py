# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 09:43:14 2014

@author: gabriel
"""
from isoch_likelihood import isoch_likelihood as i_l
import random
import numpy as np


def encode(n_bin, p_delta, p_mins, int_popul):
    '''
    Encode the solutions into binary string chromosomes to be bred.
    '''
    #delta_m, delta_a, delta_e, delta_d = (mm_m[1] - mm_m[0]), \
    #(mm_a[1] - mm_a[0]), (mm_e[1] - mm_e[0]), (mm_d[1] - mm_d[0])

    chromosomes = []
    for sol in int_popul:
        # Convert floats to binary strings.
        p_binar = []
        for i, p_del in enumerate(p_delta):
            p_binar.append(str(bin(int(((sol[i] - p_mins[i]) / p_delta[i]) *
                (2 ** n_bin))))[2:].zfill(n_bin))

        #m_binar = str(bin(int(((sol[0] - mm_m[0]) / delta_m) *
        #(2 ** n))))[2:].zfill(n)

        #a_binar = str(bin(int(((sol[1] - mm_a[0]) / delta_a) *
        #(2 ** n))))[2:].zfill(n)

        #e_binar = str(bin(int(((sol[2] - mm_e[0]) / delta_e) *
        #(2 ** n))))[2:].zfill(n)

        #d_binar = str(bin(int(((sol[3] - mm_d[0]) / delta_d) *
        #(2 ** n))))[2:].zfill(n)

        # Combine binary strings to generate chromosome.
        chrom = ''.join(p_binar)
        print 'encode', sol, p_binar, chrom
        chromosomes.append(chrom)

    return chromosomes


def chunker(seq, size):
    '''
    Helper function for 'crossover'. Returns elements in list in "chunks"
    rather than one at a time.
    '''
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def crossover(chromosomes, p_cross, cr_sel):
    '''
    Applies the crosssover operator over each chromosome.
    '''
    cross_chrom = []
    # Take two chromosomes at a time.
    for chrom_pair in chunker(chromosomes, 2):
        r = random.random()
        if r <= p_cross:

            if cr_sel == '1P':
                # Select one random crossover point.
                cp = random.randint(0, len(chrom_pair[0]))
                # Apply crossover on these two chromosomes.
                cross_chrom.append(chrom_pair[0][:cp] + chrom_pair[1][cp:])
                cross_chrom.append(chrom_pair[1][:cp] + chrom_pair[0][cp:])
            elif cr_sel == '2P':
                # Select two random crossover points.
                cp0, cp1 = np.sort(random.sample(range(0, len(chrom_pair[0])),
                                                 2))
                # Apply crossover on these two chromosomes.
                print chrom_pair
                print cp0, cp1
                cross_chrom.append(chrom_pair[0][:cp0] +
                chrom_pair[1][cp0:cp1] + chrom_pair[0][cp1:])
                cross_chrom.append(chrom_pair[1][:cp0] +
                chrom_pair[0][cp0:cp1] + chrom_pair[1][cp1:])
        else:
            # Skip crossover operation.
            cross_chrom.append(chrom_pair[0])
            cross_chrom.append(chrom_pair[1])
    return cross_chrom


def mutation(cross_chrom, p_mut):
    '''
    Applies the mutation operator over random genes in each chromosome.
    '''
    # For each chromosome flip their genes according to the probability p_mut.
    for i, elem in enumerate(cross_chrom):
        cross_chrom[i] = ''.join(char if random.random() > p_mut else
        str(1 - int(char)) for char in elem)
    return cross_chrom


def decode(param_values, n_bin, p_delta, p_mins, mut_chrom):
    '''
    Decode the chromosomes into its real values to be evaluated by the
    objective function.
    '''
    #delta_m, delta_a, delta_e, delta_d = (mm_m[1] - mm_m[0]), \
    #(mm_a[1] - mm_a[0]), (mm_e[1] - mm_e[0]), (mm_d[1] - mm_d[0])

    # Initialize empty list with as many sub-lists as parameters.
    p_lst = [[] for _ in range(len(param_values))]

    for chrom in mut_chrom:
        # Split chromosome string.
        chrom_split = [chrom[i:i + n_bin] for i in xrange(0, len(chrom), n_bin)]

        # Convert each binary into an integer for all parameters.
        #km, ka, ke, kd = (int(i, 2) for i in chrom_split)
        b2i = [int(i, 2) for i in chrom_split]

        # Map integers to the real parameter values.
        for i, p_del in enumerate(p_delta):
            # Map integer to the real parameter value.
            p_r = p_mins[i] + (b2i[i] * p_del / (2 ** n_bin))
            # Find the closest value in the parameters list.
            p = min(param_values[i], key=lambda x: abs(x - p_r))
            # Store this last value.
            p_lst[i].append(p)

        #xm = mm_m[0] + (km * delta_m / (2 ** n_bin))
        #xa = mm_a[0] + (ka * delta_a / (2 ** n_bin))
        #xe = mm_e[0] + (ke * delta_e / (2 ** n_bin))
        #xd = mm_d[0] + (kd * delta_d / (2 ** n_bin))

        # Find the closest values in the parameters list and store its index
        # in the case of metallicity and age and real values for extinction
        # and distance modulus.
        #m = min(flat_ma[0], key=lambda x: abs(x - xm))
        #a = min(flat_ma[1], key=lambda x: abs(x - xa))
        #e = min(isoch_ed[0], key=lambda x: abs(x - xe))
        #d = min(isoch_ed[1], key=lambda x: abs(x - xd))

        # Find the indexes for these metallicity and age values.
        #[m, a] = next(((i, j) for i, x in enumerate(isoch_ma) for j, y in
        #enumerate(x) if y == [m, a]), None)

        # Append indexes (for m,a) and real values (for e,d) to lists.
        #ma_lst.append([m, a])
        #e_lst.append(e)
        #d_ls.append(d)

    return p_lst


def elitism(best_sol, p_lst):
    '''
    Pass the best n_el solutions unchanged to the next generation.
    '''

    p_lst_r = []
    for sol in best_sol:
        for i, pars in enumerate(p_lst):
            p_lst_r.append([sol[i]] + pars[len(best_sol):])

        #p_lst_r.append([sol[0]] + p_lst[0][len(best_sol):])
        #p_lst_r.append([sol[1]] + p_lst[1][len(best_sol):])
        #p_lst_r.append([sol[2]] + p_lst[2][len(best_sol):])
        #p_lst_r.append([sol[3]] + p_lst[3][len(best_sol):])
    #i = 0
    #for sol in best_sol:
        ## Find indexes for these values.
        #[m, a] = next(((i, j) for i, x in enumerate(isoch_ma) for j, y in
                #enumerate(x) if y == [sol[0], sol[1]]), None)
        ## Store met and age indexes.
        #ma_lst[i] = [m, a]
        ## Store extinction and distance modulus values.
        #e_lst[i], d_lst[i] = sol[2], sol[3]
        #p_lst_r[i] =
        #i += 1

    return p_lst_r


def selection(generation, breed_prob):
    '''
    Select random chromosomes from the chromosome list passed according to
    the breeding probability given by their fitness.
    '''
    select_chrom = []
    # Draw len(generation) random numbers uniformelly distributed between [0,1)
    ran_lst = np.random.uniform(0, sum(breed_prob), len(generation))
    # For each of these numbers, obtain the corresponding likelihood from the
    # breed_prob CDF.
    gen_breed = zip(*[generation, breed_prob])
    for r in ran_lst:
        s = 0.
        for sol, num in gen_breed:
            s += num
            if s >= r:
                select_chrom.append(sol)
                break

    return select_chrom


def evaluation(err_lst, obs_clust, completeness, isoch_list, param_values,
                 p_lst, sc_params, isoch_done, cmd_sel):
    '''
    Evaluate each random isochrone in the objective function to obtain
    the fitness of each solution.
    '''
    likelihood, generation_list = [], []
    # Process each isochrone selected.
    for params in zip(*p_lst):

        ## Metallicity and age indexes.
        m_i = param_values[0].index(params[0])
        a_i = param_values[1].index(params[1])
        #d = d_lst[indx]
        ## Pass metallicity and age values for plotting purposes.
        #params = [isoch_ma[m][a][0], isoch_ma[m][a][1], e, d]

        # Check if this isochrone was already processed.
        if params in isoch_done[0]:
            # Get likel_val value for this isochrone.
            likel_val = isoch_done[1][isoch_done[0].index(params)]
        else:
            isochrone = isoch_list[m_i][a_i]
            # Call likelihood function with m,a,e,d values.
            likel_val = i_l(err_lst, obs_clust, completeness, sc_params,
                            isochrone, params, cmd_sel)
            # Append data identifying the isochrone and the obtained
            # likelihood value to this *persistent* list.
            isoch_done[0].append(params)
            isoch_done[1].append(likel_val)

        # Append same data to the lists that will be erased with each call
        # to this function.
        generation_list.append(params)
#        likelihood.append(round(likel_val, 2))
        likelihood.append(likel_val)

    # Sort according to the likelihood list.
    generation = [x for y, x in sorted(zip(likelihood, generation_list))]

    # For plotting purposes: sort list in place putting the likelihood minimum
    # value first.
    likelihood.sort()

    return generation, likelihood, isoch_done


def random_population(param_values, n_ran):
    '''
    Generate a random set of parameter values to use as a random population.
    '''
    # Pick n_ran initial random solutions from each list storing all the
    # possible parameters values. These lists store real values.
    p_lst = []
    for param in param_values:
        p_lst.append([random.choice(param) for _ in range(n_ran)])

    #e_lst = [random.choice(isoch_ed[0]) for _ in range(n_ran)]
    #d_lst = [random.choice(isoch_ed[1]) for _ in range(n_ran)]
    ## Flat array so every [metal,age] combination has the same probability
    ## of being picked. This list stores indexes.
    #ma_flat = [(i, j) for i in range(len(isoch_ma)) for j in
    #range(len(isoch_ma[i]))]
    #ma_lst = [random.choice(ma_flat) for _ in range(n_ran)]

    return p_lst


def num_binary_digits(param_rs):
    '''
    Store parameters ranges and calculate the minimum number of binary digits
    needed to encode the solutions.
    '''

    p_mins, p_delta, p_step = [], [], []
    for param in param_rs:
        p_mins.append(param[0])  # Used by the encode operator.
        p_delta.append(param[1] - param[0])  # max - min value
        p_step.append(param[2])  # step
    #mm_m, step_m = [ranges_steps[0][0], ranges_steps[0][1]], ranges_steps[0][2]
    #mm_a, step_a = [ranges_steps[1][0], ranges_steps[1][1]], ranges_steps[1][2]
    #mm_e, step_e = [ranges_steps[2][0], ranges_steps[2][1]], ranges_steps[2][2]
    #mm_d, step_d = [ranges_steps[3][0], ranges_steps[3][1]], ranges_steps[3][2]

    #delta_m, delta_a, delta_e, delta_d = (mm_m[1] - mm_m[0]), \
    #(mm_a[1] - mm_a[0]), (mm_e[1] - mm_e[0]), (mm_d[1] - mm_d[0])
    p_interv = np.array(p_delta) / np.array(p_step)

    # Number of binary digits used to create the chromosomes.
    n_bin = int(np.log(max(p_interv)) / np.log(2)) + 1

    return n_bin, p_delta, p_mins


def gen_algor(flag_print_perc, err_lst, obs_clust, completeness, ip_list,
    sc_params, ga_params, cmd_sel):
    '''
    Genetic algorithm adapted to find the best fit model-obervation.
    '''

    # Unpack.
    isoch_list, param_values, param_rs = ip_list
    n_pop, n_gen, fdif, p_cross, cr_sel, p_mut, n_el, n_ei, n_es = ga_params

    # Check if n_pop is odd. If it is sum 1 to avoid conflict if cr_sel
    # '2P' was selected.
    n_pop += n_pop % 2

    # Get number of binary digits to use.
    n_bin, p_delta, p_mins = num_binary_digits(param_rs)

    # Flat out metallicity and ages list (used by the 'Decode' process).
    #flat_ma = zip(*list(itertools.chain(*isoch_ma)))

    # Fitness.
    # Rank-based breeding probability. Independent of the fitness values,
    # only depends on the total number of chromosomes n_pop and the fitness
    # differential fdif.
    fitness = [1. / n_pop + fdif * (n_pop + 1. - 2. * (i + 1.)) /
    (n_pop * (n_pop + 1.)) for i in range(n_pop)]

    ### Initial random population evaluation. ###
    p_lst_r = random_population(param_values, n_pop)
    print 'rad1', p_lst_r, '\n'

    # Stores parameters of the solutions already processed and the likelihhods
    # obtained.
    isoch_done = [[], []]

    # Evaluate initial random solutions in the objective function.
    generation, lkl, isoch_done = evaluation(err_lst, obs_clust,
        completeness, isoch_list, param_values, p_lst_r,
        sc_params, isoch_done, cmd_sel)
    print 'eval1', generation, '\n'

    # Store best solution for passing along in the 'Elitism' block.
    best_sol = generation[:n_el]
    print 'best sol1', best_sol, '\n'

    # For plotting purposes.
    lkl_old = [[], []]
    # Stores indexes where the Ext/Imm operator was applied.
    ext_imm_indx = []

    # Initiate counters.
    best_sol_count, ext_imm_count = 0, 0
    # Initiate empty list. Stores the best solution found after each
    # application of the Extinction/Immigration operator.
    best_sol_ei = []

    # Print percentage done.
    milestones = [25, 50, 75, 100]
    # Begin processing the populations up to n_gen generations.
    for i in range(n_gen):

        #### Selection/Reproduction ###
        # Select chromosomes for breeding from the current generation of
        # solutions according to breed_prob to generate the intermediate
        # population.
        int_popul = selection(generation, fitness)
        print 'int pop', int_popul, '\n'

        # Encode intermediate population's solutions into binary chromosomes.
        chromosomes = encode(n_bin, p_delta, p_mins, int_popul)
        print 'chrom', chromosomes, '\n'

        #### Breeding ###
        # Pair chromosomes by randomly shuffling them.
        random.shuffle(chromosomes)

        # Apply crossover operation on each subsequent pair of chromosomes
        # with a p_cross probability (crossover probability)
        cross_chrom = crossover(chromosomes, p_cross, cr_sel)

        # Apply mutation operation on random genes for every chromosome.
        mut_chrom = mutation(cross_chrom, p_mut)

        ### Evaluation ###
        # Decode the chromosomes into solutions to form the new generation.
        p_lst_d = decode(param_values, n_bin, p_delta, p_mins, mut_chrom)

        # Elitism: make sure that the best n_el solutions from the previous
        # generation are passed unchanged into this next generation.
        p_lst_e = elitism(best_sol, p_lst_d)
        print 'eli', p_lst_e, '\n'

        # Evaluate each new solution in the objective function and sort
        # according to the best solutions found.
        generation, lkl, isoch_done = evaluation(err_lst, obs_clust,
        completeness, isoch_list, param_values, p_lst_e, sc_params,
        isoch_done, cmd_sel)
        print 'eval2', generation[0], '\n'

        ### Extinction/Immigration ###
        # If the best solution has remained unchanged for n_ei
        # generations, remove all chromosomes but the best ones (extinction)
        # and fill with random new solutions (immigration).

        # Check if new best solution is equal to the previous one.
        if generation[0] == best_sol[0]:
            # Increase counter.
            best_sol_count += 1

            # Check how many times the best_sol has remained unchanged.
            if best_sol_count == n_ei:
                # Apply Extinction/Immigration operator.

                ### Exit switch. ##
                # If n_es runs of the Ext/Imm operator have been applied with
                # no changes to the best solution, exit the GA.
                if best_sol[0] == best_sol_ei:
                    # Increase Ext/Imm operator counter.
                    ext_imm_count += 1
                    if ext_imm_count == n_es:
                        # Exit generations loop.
                        break
                else:
                    # Update best solution.
                    best_sol_ei = best_sol[0]
                    # Reset counter.
                    ext_imm_count = 0

                # Generate (n_pop-n_el) random solutions.
                p_lst_r = random_population(param_valules, (n_pop - n_el))
                # Store random solutions in random order.
                generation_ei = []
                for indx, ma in enumerate(ma_lst):
                    m, a = ma[0], ma[1]
                    e, d = e_lst[indx], d_lst[indx]
                    generation_ei.append([isoch_ma[m][a][0], isoch_ma[m][a][1],
                                          e, d])
                # Append immigrant population to the best solution.
                generation = best_sol + generation_ei
                # Reset best solution counter.
                best_sol_count = 0

                # For plotting purposes. Save index where the operator was used.
                ext_imm_indx.append([i])

        else:
            # Update best solution for passing along in the 'Elitism' block.
            best_sol = generation[:n_el]
            # Reset counter.
            best_sol_count = 0

        if flag_print_perc:
            percentage_complete = (100.0 * (i + 1) / n_gen)
            while len(milestones) > 0 and percentage_complete >= milestones[0]:
                print "  {}% done".format(milestones[0])
                # Remove that milestone from the list.
                milestones = milestones[1:]

        # For plotting purposes.
        lkl_old[0].append(lkl[0])
        lkl_old[1].append(np.mean(lkl))

    isoch_fit_params = [generation[0], lkl_old, ext_imm_indx, isoch_done]

    return isoch_fit_params
