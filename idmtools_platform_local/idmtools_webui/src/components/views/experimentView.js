
import React from "react";
import { withStyles } from '@material-ui/core/styles';
import { connect } from "react-redux";
import { fetchExperiments, deleteExperiment } from "../../redux/action/experiment"
import { Table, TableHead, TableCell, TableRow, TableBody, Paper, Button, Typography, Divider,
    Card, CardContent, List, ListItem, ListItemText, TextField } from "@material-ui/core";

import {formatDateString} from  "../../utils/utils";
import FolderIcon from "@material-ui/icons/Folder";
import SplitterLayout from 'react-splitter-layout';
import ExperimentChart from '../charts/experimentChart';
import * as _ from "lodash";




const styles = theme => ({
    folder: {
        color:'yellow'
    },
    splitter: {

        height: '100%', 
        '& .layout-pane-primary': {
            height:'100%', 
            backgroundColor:'#424242'
        },
        backgroundColor: '#424242'


        
    },
    details: {
        height:'100%'
    },
    root: {
        height:'100%'
    },
    cardTitle: {
       color: '#2196f3',
       padding: 10
    },
    textField: {
        marginLeft: theme.spacing(1),
        marginRight: theme.spacing(1),
        width: 200,
      },
    itemText: {
        maxWidth:200
    },
    itemValue: {
        maxWidth:400
    },
     details: {
         margin:30
     },
     highlight:{
         backgroundColor:'#43a047'
     }
})

class ExperimentView extends React.Component {


    constructor(props) {
        super(props);
        this.state = {
            selectedExp : null
        }
        this.rowClick = this.rowClick.bind(this);
        this.deleteExp = this.deleteExp.bind(this);
    }

    componentDidMount() {
        const { dispatch } = this.props;
        dispatch(fetchExperiments());

    }
    rowClick(e) {
        //debugger
        this.setState( {
            selectedExp : e.currentTarget.getAttribute("exp_id") == this.state.selectedExp ? null : e.currentTarget.getAttribute("exp_id")
        });
    }

    deleteExp(e) {
        e.stopPropagation();
        e.preventDefault();

        const { dispatch } = this.props;

        dispatch(deleteExperiment(e.currentTarget.getAttribute("exp_id")));
        
        return false;
    }



    render() {
        const { experiments, classes } = this.props;

        let sorted = [];

        let status, command, tags
        
        if (this.props.experiments.experiments) 
            sorted = _.reverse(_.sortBy(this.props.experiments.simulatexperimentsions, (o) => {
                return o.created;
            }));

        var progressStr = (progressObj) => {
            //debugger
            if (progressObj && progressObj.length > 0) {
                let progress = progressObj[0]
                return ("Done:" + (progress["done"] ? progress["done"] : "0") + " " + 
                        "Created:" + (progress["created"] ? progress["created"] : "0") + " " +
                        "In progress:" + (progress["in_progress"] ? progress["in_progress"] : "0") )
            } else
                return ""

        }
        
        if (this.state.selectedExp) {
            
            let index = _.findIndex(this.props.experiments.experiments, {experiment_id: this.state.selectedExp});
            let exps = this.props.experiments.experiments
            status = JSON.stringify(exps[index].progress);
            command =  ""; //exps[index].extra_details.command;
            tags = JSON.stringify( exps[index].tags);
        }

        return (
            <div className={classes.splitter} ref={(ref) => this.scrollParentRef = ref}>
            <SplitterLayout vertical="false" className={classes.splitter} percentage="true" secondaryInitialSize="60">
                <Paper className={classes.root}>
                    <ExperimentChart/>
                </Paper>
                
                <SplitterLayout vertical="false" percentage="true" secondaryInitialSize="50">

                    <Paper className={classes.root}>
                        <Table className={classes.table}>
                            <TableHead>
                                <TableRow>
                                    <TableCell align="right">Experiment ID</TableCell>
                                    <TableCell align="right">Status</TableCell>
                                    <TableCell align="right">Folder</TableCell>
                                    <TableCell align="center">Action</TableCell>
                                    <TableCell align="right">Created</TableCell>
                                    <TableCell align="right">Updated</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {experiments && experiments.experiments && experiments.experiments.map(exp => (
                                    <TableRow key={exp.experiment_id} onClick={this.rowClick} exp_id={exp.experiment_id} className={exp.experiment_id == this.state.selectedExp ? classes.highlight: null}>

                                        <TableCell align="right">{exp.experiment_id}</TableCell>
                                        <TableCell align="right">{progressStr(exp.progress)}</TableCell>
                                        <TableCell align="right">
                                            <a target="_blank" href={'http://' + window.location.hostname + ':5000' + exp.data_path}>
                                            <FolderIcon className={classes.folder}/>
                                            </a>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Button className={classes.cancel} color="secondary" exp_id={exp.experiment_id} onClick={this.deleteExp}>Delete</Button>

                                        </TableCell>
                                        <TableCell align="right">{formatDateString(exp.created)}</TableCell>
                                        <TableCell align="right">{formatDateString(exp.updated)}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Paper>
                    { 
                        this.state.selectedExp &&
                        <Paper className={classes.details}>
                            <Card className = {classes.card}>
                                <CardContent>
                                    
                                    <Typography variant="h5" className={classes.cardTitle}>Details</Typography>
                                    <Divider/>
                                    <List>
                                        <ListItem>
                                            <ListItemText className={classes.itemText}>Id:</ListItemText>
                                            <ListItemText className={classes.itemValue}>{this.state.selectedExp}</ListItemText>
                                        </ListItem>
                                        <ListItem >
                                            <ListItemText className={classes.itemText}>Status</ListItemText>
                                            <ListItemText className={classes.itemValue}>{status}</ListItemText>
                                        </ListItem>
                                        <ListItem >
                                            <ListItemText className={classes.itemText}>Command</ListItemText>
                                            <ListItemText className={classes.itemValue}>{command}</ListItemText>
                                        </ListItem>
                                        <ListItem >
                                            <ListItemText className={classes.itemText}>Tags</ListItemText>
                                            <ListItemText className={classes.itemValue}>{tags}</ListItemText>
                                        </ListItem>

                                    </List>
                                </CardContent>
                            </Card>
                        </Paper>
                    }
                    </SplitterLayout>
            </SplitterLayout>
            </div>
        )
    }

}

function mapStateToProps(state) {
    
    return ({

        experiments: state.experiments
    })

}

export default connect(mapStateToProps)(withStyles(styles, { withTheme: true })(ExperimentView));
