
source /root/watchoptical/build/rat-pac/../../env.sh
TMPNAME=$(date +%s%N)
rat attenuation_1e-12_scattering_None.mac _linktoconfig.mac  mac/detector_Watchman.mac mac/process_Watchman.mac mac/phys_heysham_background.mac mac/geo_LIQUID.mac mac/rates_Watchman_heysham_background_LIQUID_pn_ibd.mac -o test.root -l test.log'

