import time
import json
import pandas as pd
import numpy as np
from graph_maker import dict_dataframer, plotter
from blkx_parsers import fm_parser, central_parser
from plane_power_calculator import power_curve_culator, enginecounter
from ram_pressure_density_calculator import rameffect_er

"""
Script used for locally making engine power plots, based on flightmodel files from .
Alows to simultaneously plot engine power logged in-game using WTRTI, if log file directory is referenced in TEST_file_dir variable.

Useful for development and debugging functions from 'plane_power_calculator' 
and other scripts, by comparing calulated plots with ones made from in-game logged files.

Current issues in 'plane_power_calculator':
 - P-63 A-5 A-10 and C5 aren't accurately modelled above critial altitudes. 
 - TU-1 is almost good.

Make sure you have downloaded necessary flighmodel files via 'batch_runner.py' script into the input_files directory.
"""

def inputter():
    """
    All parameters for customization of the power plot made locally. Used only within this script.

    Returns:
        tuple: a tuple of all the necessary parameters passed to main.
        """
    plot_all_planes = False
    speed = 280
    speed_type = "IAS"
    air_temp = 15
    air_temp_unit= '°C'
    octane = True
    power_to_weight = False
    engine_modes = [
        "100%",
        "WEP"
        ]
    max_altm = 15000
    alt_unit = 'm'
    speed_unit = 'kph'

    axis_layout= False
    alt_tick = 10
    fm_dir = "input_files/fm_files/"
    central_dir = "input_files/central_files/"
    central_fm_read_dir = "output_files/plane_name_files/central-fm_plane_names_piston.json"
    plot_t = "power"
    
    TEST_file_dir = [
    # "ingame_power_log_files/Bf-109G-2_1.91_climb_to_8k_270IAS.csv",
    # "ingame_power_log_files/saab_b18b-2023_04_280IAS.csv",
    "ingame_power_log_files/ta-152h-1-2021_03_climb_to_14k_GM1_265IAS.csv",
    # "ingame_power_log_files/ki-83-2023_04_285IAS.csv",
    # "ingame_power_log_files/tempest_mk2-2022_11_280IAS.csv",
    # "ingame_power_log_files/p-63a-5-2023_05_500TAS.csv",
    # "ingame_power_log_files/p-63a-10-2023_05_100%&WEP_280IAS.csv",
    # "ingame_power_log_files/p-63a-10-2023_05_500TAS.csv",
    # "ingame_power_log_files/p-63c-5-2023_05_100%_280IAS.csv",
    # "ingame_power_log_files/p-63c-5-2023_05_WEP_280IAS.csv",
    # "ingame_power_log_files/tu-1-2023_10_WEP_700tas_12k.csv",
    # "ingame_power_log_files/tu-1-2023_10_100%_700tas_8k.csv",
    # put your new test flight climb logs to compare with the calculator here
    ]

    fm_files = [
    #####Those need improvement:
    # "p-63a-10",
    # "p-63c-5",
    # "p-63a-5",
    # "tu-1",
    #####Afaik, all other planes are accurately calculated

    ### GERMANY
    # "bf-109E-4",
    # "bf-109f-1",
    # "bf-109f-4_trop",
    # "bf-109f-4",
    # "bf-109g-2",
    # "bf-109g-6",
    # "bf-109g-10",
    # "bf-109g-14",
    # "bf-109g-14as",
    # "bf-109k-4",
    # "me_264",
    # "ta_152c",
    "ta-152h-1",
    # "fw-190d-12",
    # "fw-190f-8",
    # "fw-190a-5",
    # "fw-190a-1",
    # "fw-190c",
    # "me-410a-1",
    # "ju-388j",
    # "do_335a_0",
    # "bv-155b-1",
    # "bf-109z",
    # "pyorremyrsky",

    ## JAPAN
    # "b7a2_homare_23",
    # "b7a2",
    # 'j2m2',
    # 'j2m3',
    # 'j2m5',
    # 'j2m5_30mm',
    # 'j2m4_kai',
    # 'j2m5',

    # "ki-83",
    # "ki_94_2",
    # "ki_84_ko",
    # "j6k1",
    # "a7m2",
    # "ki_44_2_hei",
    # "ki_43_2",
    # "ki_43_1",
    # "ki_100_early",
    # "ki_100_2",
    # "ki_61_1a_ko",
    # "ki_61_1a_hei",
    # "ki_61_1a_tei",
    # "ki_61_1a_otsu",
    # "ki_87",
    # "ki_94_2",
    # "ki_61_1a_ko",
    # "ki_61_2_early",
    # "d4y1",

    ###  USA
    # "f4u-4b",
    # "f8f1b",
    # "f2g-1",
    # "corsair_fmk2",
    # "f4u-4",
    # "f4u-6_au-1",
    # "f4u-1a",
    # "am_1_mauler",
    # "pbm_1",

    # "p-51b",
    # "p-51_mk1a_usaaf",
    # "xp-55",
    # "p-51d-5",
    # "p-51c-10-nt",
    # "p-51d-30_usaaf_korea",
    # "p-38g",
    # "p-38l",
    # "p-38k",
    
    # "xp-50",
    # "xf5f",
    # "douglas_ad_2",
    # "am_1_mauler",

    # "p-39n",
    # "p-63a-10",
    # "p-63c-5",
    # "p-63a-5",
    # "p-47d",
    # "p-47d_22_re",
    # "p-47d-28",
    # "p-47d-28",
    # "p-47m-1-re",
    # "b_26b_c",
    # "b-17e",

    ###  GREAT BRITAIN
    # "sea_fury_fb11",
    # "hornet_mk3",
    # "shackleton_mr_mk_2",
    # "tempest_mk2",
    # "tempest_mkv",
    # "MB_5",
    # "stirling_mk3",
    # "typhoon_mk1b_late",
    # "typhoon_mk1b",
    # "typhoon_mk1a",
    
    # "spitfire_mk1",
    # "spitfiremkiia",
    # "seafire_mk3",
    # "spitfire_mk5b_notrop",
    # "spitfire_mk5c",
    # "spitfire_ix_early",
    # "spitfire_ix",
    # "spitfire_ix_cw",
    # "spitfire_xvi",
    # "spitfire_fr_mk14e",
    # "spitfire_mk14e",
    # "seafire_mk17",
    # "spitfire_mk18e",
    # "spitfire_f22",
    # "spitfire_f24",
    # "seafire_fr47",
    # "boomerang_mki",

    # ###  ITALY
    # "g_55_serie1",
    # "mc-205_serie1",
    # "sm_91",
    # "re_2001_cb",
    # "mc-202",

    #  ### SWEDEN
    # "saab_b18b",
    # "saab_j21a_1",
    
    #  ### USSR
    # "i_185_m82",
    # "i-153_m62",
    # "itp-m1",
    # "la-5_type37_early",
    # "mig_3_series_34",
    # "mig_3_series_1_15_bk_pod",
    # "yak-3u",
    # "yak-3",
    # "yak-3_vk107",
    # "po-2",
    # "yak-9u",
    # "la-7",
    # "su-2_tss1",
    # "su-2_mv5",
    # "su-2_m82",
    # "bb-1",
    # "pe-2-205",
    # "tu-2_postwar_late",
    # "tu-2_postwar",
    # "tu-2",

    ### FRANCE
    # "cr_32",
    # "cr_32_quater",
    # "d_371",
    # "d_373",
    # "d_500",
    # "d_501",
    # "d_510",
    # "d_520",
    # "d_521",
    # "mb_152c1",
    # "mb_175t",
    # "so_8000_narval",
    # "vb_10_02",
    # "mb_157",
    # "ms_405",
    # "ms_406c1",
    # "ms_410c1",

    # "",
    # "",
    # "",
    # "",
    # "",
    # "",
    # "",
    ]

    return (speed, speed_type, air_temp, octane, power_to_weight, engine_modes, alt_tick, fm_dir, central_dir, central_fm_read_dir,
            max_altm, alt_unit, speed_unit, air_temp_unit, axis_layout, plot_t, plot_all_planes, fm_files, TEST_file_dir)

def csv_dataframer(TEST_file_dir):
    """
    Converts .csv files containing logs from in-game testing to a dataframe with only altitude and horsepower columns.
    """
    TEST_dataf_all = pd.DataFrame(index=np.arange(12000))
    for file_index, directory in enumerate(TEST_file_dir):
        filename = directory.rsplit('/', 1)[-1]
        planename = filename.rsplit('.', 1)[0]
        TEST_dataf = pd.read_csv(directory)
        TEST_dataf = TEST_dataf.drop(TEST_dataf[TEST_dataf["Altitude, m"] < 50].index) #remove takeoff disturbances
        Power_cols = [col for col in TEST_dataf.columns if col.startswith('Power')]

        if not Power_cols:
            return "The test files don't contain columns with 'Power' in them"
        for engine_index, column in enumerate(Power_cols):

            if "Power" in column:
                TEST_dataf_all = TEST_dataf_all.assign(col=TEST_dataf[column])

                TEST_dataf_all = TEST_dataf_all.rename(
                    columns={"col": "TestPower" + str(file_index) + str(planename) + str(engine_index)})
        TEST_dataf_all = TEST_dataf_all.assign(col=TEST_dataf["Altitude, m"])
        TEST_dataf_all = TEST_dataf_all.rename(columns={"col": "Altitude, m" + str(file_index)})
    return TEST_dataf_all


def dataframe_combiner(MODEL_dataf_all, TEST_dataf_all):
    """
    Combines dataframe with calculated power curves and a dataframe with power curves from in-game tests
    """
    
    if MODEL_dataf_all.empty:
        return TEST_dataf_all
    elif TEST_dataf_all.empty:
        return MODEL_dataf_all
    elif len(TEST_dataf_all.index) >= len(MODEL_dataf_all.index): #Make shorter thing join to the longer thing - no cut
        MODEL_TEST_dataf = TEST_dataf_all.join((MODEL_dataf_all),)
    else:
        MODEL_TEST_dataf = MODEL_dataf_all.join((TEST_dataf_all),)
    return MODEL_TEST_dataf


def main():
    """
    Runs all functions needed to locally run engine power calcuation ond display resulting plots in the browser.
    """
    start_time = time.time()
    (speed, speed_type, air_temp, octane, power_to_weight, engine_modes, alt_tick, fm_dir, central_dir, central_fm_read_dir,
     max_altm, alt_unit, speed_unit, air_temp_unit, axis_layout, plot_t, plot_all_planes, fm_files, TEST_file_dir) = inputter()

    
    if plot_all_planes == True:
        with open(central_fm_read_dir, "r") as central_to_FM_json:
            planes_to_calculate = json.load(central_to_FM_json)
    else:
        planes_to_calculate = fm_files
    named_central_dict = central_parser(central_dir, planes_to_calculate, central_fm_read_dir, ".blkx")
    named_fm_dict = fm_parser(fm_dir, planes_to_calculate, central_fm_read_dir)
    
    named_power_curves_merged, plane_speed_multipliers = power_curve_culator(named_fm_dict,
                                                                                named_central_dict, 0,
                                                                                speed_type, air_temp,
                                                                                octane,
                                                                                engine_modes,
                                                                                1) 
    #above alt_tick = 1 because otherwise the power_curves_merged[user_alt] = power_curves_merged_unrammed[(alt_RAM + 4000)] will fail
    #it's because power_curves_merged_unrammed indexes are treated as meters, but is alt tick = 10, then each index is 10m.
    # otherwise of you want this alt_tick to be 10, then use 'int(round(((alt_RAM + 4000)/10),0))' istead of (alt_RAM + 4000)! 
    for (plane_name, power_curves_merged_old), (plane_name2, speed_multiplier_float) in zip(named_power_curves_merged.items(), plane_speed_multipliers.items()):
        speed_multiplier = {}
        for mode, power_curves_merged_unrammed in power_curves_merged_old.items():
            power_curves_merged = {}
            for user_alt in range(0, max_altm, alt_tick):
                alt_RAM = (rameffect_er(user_alt, air_temp, speed, speed_type, speed_multiplier_float))
                try:
                    power_curves_merged[user_alt] = power_curves_merged_unrammed[(alt_RAM + 4000)] 
                except KeyError:
                    continue #If engine power is 0, the dictionary ends, so you can't apply RAM effect.
            named_power_curves_merged[plane_name][mode] = power_curves_merged
    MODEL_dataf_all = dict_dataframer(named_power_curves_merged, alt_unit)
    TEST_dataf = csv_dataframer(TEST_file_dir)
    pd.set_option('display.max_columns', None)
    MODEL_TEST_dataf = dataframe_combiner(MODEL_dataf_all, TEST_dataf)
    final_plot = plotter(MODEL_TEST_dataf, max_altm, alt_unit, speed, speed_type, speed_unit, air_temp,
                         air_temp_unit, axis_layout, plot_t)
    
    plane_engine_count = enginecounter(named_fm_dict)
    'Post-processing into a dataframe and plot generation'

    print("--- %s seconds ---" % (time.time() - start_time))
    return

if __name__ == "__main__":
    main()