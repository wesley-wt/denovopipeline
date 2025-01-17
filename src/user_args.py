import argparse
import sys
import logging
from preprocess import reformat_MGF, denovo_setup
from denovo import denovo_seq


logger = logging.getLogger(__name__)


def setup(test_argv=None):
    parser = argparse.ArgumentParser(
        description="De Novo Sequencing Pipeline for peptide prediction and assembly of full-protein sequences by"
        "tandem mass spectrometry."
    )
    subparsers = parser.add_subparsers(dest="subparser_name")
    reformatMGF_parser = subparsers.add_parser(
        "reformatMGF",
        help="Formatting MGF files to be compatible with all de novo tools. Indices are changed from 0 to N.",
    )
    reformatMGF_parser.add_argument("-i", "--input", help="Input MGF file")

    denovosequencing_parser = subparsers.add_parser(
        "denovo", help="Start the de novo sequencing analysis"
    )
    denovosequencing_parser.add_argument(
        "-i", "--input", help="Input reformatted MGF file"
    )
    denovosequencing_parser.add_argument("-o", "--output", help="result directory")
    denovosequencing_parser.add_argument(
        "--denovogui",
        nargs="?",
        const=0,
        type=int,
        help="Turn Novor sequencing on or off. 1: on, " "0: off, default is 0",
    )
    denovosequencing_parser.add_argument(
        "--smsnet",
        nargs="?",
        const=0,
        type=int,
        help="Turn SMSNet sequencing on or off. 1: on, 0: off, default " "is 0",
    )
    denovosequencing_parser.add_argument(
        "--deepnovo",
        nargs="?",
        const=0,
        type=int,
        help="Turn DeepNovo sequencing on or off. 1: on, 0: off, " "default is 0",
    )
    denovosequencing_parser.add_argument(
        "--pnovo3",
        nargs="?",
        const=0,
        type=int,
        help="Turn pNovo3 sequencing on or off. 1: on, 0: off, default " "is 0",
    )
    denovosequencing_parser.add_argument(
        "--pointnovo",
        nargs="?",
        const=0,
        type=int,
        help="Turn PointNovo sequencing on or off. 1: on, 0: off, default " "is 0",
    )
    denovosequencing_parser.add_argument(
        "--casanovo",
        nargs="?",
        const=0,
        type=int,
        help="Turn Casanovo sequencing on or off. 1: on, 0: off, default " "is 0",
    )
    denovosequencing_parser.add_argument(
        "--params",
        default="resources/DeNovoGUI-1.16.6/newparameter.par",
        type=str,
        help="Location of Parameter File for DeNovoCli. See documentation of "
        "DeNovoGUI for building paramter. If none is given it will use "
        "resources/DeNovoGUI-1.16.6/newparameter.par",
    )
    denovosequencing_parser.add_argument(
        "--smsnet_model",
        default="resources/SMSNet/MassIVE_HCD/",
        type=str,
        help="Location of Model for SMSNet. If none is given it will use "
        "resources/SMSNet/MassIVE_HCD",
    )
    denovosequencing_parser.add_argument(
        "--deepnovo_model",
        default="MassIVE_HCD",
        type=str,
        help="Location of Model for DeepNovo (PNAS). If none is given it will use resources/DeepNovo_Antibody/MassIVE_HCD",
    )
    denovosequencing_parser.add_argument(
        "--pointnovo_model",
        default="models/PointNovo/train",
        type=str,
        help="Location of Model for PointNovo. Default: train/",
    )
    denovosequencing_parser.add_argument(
        "--casanovo_model",
        default="train",
        type=str,
        help="Location of Model for Casanovo. Default: train/",
    )
    setupdenovo_parser = subparsers.add_parser(
        "setup", help="Downloads knapsack, pre-trained models and test data"
    )
    summary_parser = subparsers.add_parser("summary", help="Create Summary File")
    summary_parser.add_argument("-i", "--input", help="Input MGF file")
    summary_parser.add_argument(
        "-r",
        "--results",
        help="Result Directory containing results from single de novo tools",
    )
    summary_parser.add_argument(
        "-db",
        "--dbreport",
        default="",
        help="Path to the exported PSM Report by PeptideShaker",
    )

    convertForALPS_parser = subparsers.add_parser(
        "assembly",
        help="Takes single results from DeNovoTools, parses them und runs ALPS for assembly",
    )
    convertForALPS_parser.add_argument("-i", "--input", help="path to summary.csv file")
    convertForALPS_parser.add_argument(
        "-k",
        "--kmer",
        help="Length of k-mers for ALPS, 6 or 7 is recommended",
        default=7,
    )
    convertForALPS_parser.add_argument(
        "-c",
        "--contigs",
        help="Number of top contigs to use for assembly of ALPS",
        default=20,
    )
    convertForALPS_parser.add_argument(
        "-q",
        "--quality-cutoff",
        help="Threshold of Quality Cutoff. All Peptides below this score will not be used for assembly.",
        default=50,
    )
    convertForALPS_parser.add_argument(
        "-s",
        "--create-stats",
        help="Option to export Stats about Recall and Precision using the results from database search",
        default=True,
    )

    args = parser.parse_args()
    if args.subparser_name == "setup":
        logger.info("Setup started")
        denovo_setup()
        sys.exit(0)
    elif args.subparser_name == "reformatMGF":
        logger.info("Formatting of MGF started")
        reformat_MGF(args.input)
        sys.exit(0)
    elif args.subparser_name == "denovo":
        logger.info("De novo sequencing started")
        if args.input == None:
            denovosequencing_parser.print_help()
        else:
            denovo_seq(
                args.input,
                args.output,
                args.denovogui,
                args.smsnet,
                args.deepnovo,
                args.pnovo3,
                args.pointnovo,
                args.casanovo,
                args.params,
                args.smsnet_model,
                args.deepnovo_model,
                args.pointnovo_model,
                args.casanovo_model
            )
        sys.exit(0)
    elif args.subparser_name == "summary":
        logger.info("Generating summary file started.")
        from createsummary import denovo_summary

        denovo_summary(args.input, args.results, args.dbreport)
        sys.exit(0)
    elif args.subparser_name == "assembly":
        from assembly import convert_For_ALPS

        logger.info("Assembly started.")
        convert_For_ALPS(
            args.input, args.kmer, args.contigs, args.quality_cutoff, args.create_stats
        )
        sys.exit(0)
    elif args.subparser_name == None:
        logger.info("Unspecified Mode.")
        parser.print_help()
        sys.exit(0)
