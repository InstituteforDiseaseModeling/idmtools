
import React from "react";
import { withStyles } from '@material-ui/core/styles';
import { connect } from "react-redux";
import { fetchExperiments, deleteExperiment } from "../../redux/action/experiment"
import { Table, TableHead, TableCell, TableRow, TableSortLabel, TableBody, Paper, Button, Typography, Divider,
    Card, CardContent, List, ListItem, ListItemText, Grid, IconButton ,
    Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from "@material-ui/core";

import {formatDateString} from  "../../utils/utils";
import FolderIcon from "@material-ui/icons/Folder";
import ClearIcon from "@material-ui/icons/Clear";
import SplitterLayout from 'react-splitter-layout';
import ExperimentChart from '../charts/experimentChart';
import * as _ from "lodash";
import {setFilter} from "../../redux/action/experiment";
import {getExperimentsByFilter} from "../../redux/selectors/experiments";


const styles = theme => ({
    folder: {
        color: 'yellow'
    },
    splitter: {

        height: '100%',
        '& .layout-pane-primary': {
            height: '100%',
            backgroundColor: '#424242'
        },
        backgroundColor: '#424242'
    },
    details: {
        height: '100%',
        margin: 30
    },
    root: {
        height: '100%'
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
        maxWidth: 200
    },
    itemValue: {
        maxWidth: 400
    },

    highlight: {
        backgroundColor: '#43a047'
    },
    clearIcon: {
        color: 'red',

    }

});

class ExperimentView extends React.Component {


    constructor(props) {
        super(props);
        this.state = {
            selectedExp : null,
            columns: [
                {name: "experiment_id" , sortOrder:  'asc', active: false, title: 'Experiment Id' },
                {name: "status" , sortOrder:  'asc', active: false, title:'Status'},
                {name: "folder" , sortOrder:  '', active: false, title: 'Folder' },
                {name: "action" , sortOrder:  '', active: false, title: "Action" },
                {name: "created" , sortOrder:  'desc', active: true, title: "Created" },
                {name: "updated" , sortOrder:  'desc', active: false, title:"Updated" }
            ],
            dialogOpen: false,
            expIdForCancel: null

        };
        this.rowClick = this.rowClick.bind(this);
        this.deleteExp = this.deleteExp.bind(this);
        this.dragEnd = this.dragEnd.bind(this);
        this.closeDetails = this.closeDetails.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.handleDialogYesClick = this.handleDialogYesClick.bind(this);
    }

    componentDidMount() {
        const { dispatch } = this.props;
        dispatch(fetchExperiments());

    }
    rowClick(e) {
        this.setState( {
            selectedExp : e.currentTarget.getAttribute("exp_id") === this.state.selectedExp ? null : e.currentTarget.getAttribute("exp_id")
        });
    }

    deleteClick(cb) {
        return (e)=> {
            e.stopPropagation();
            e.preventDefault();

            this.setState({dialogOpen:true, cb: cb, expIdForCancel:e.currentTarget.getAttribute("exp_id") });

            return false;
          }      
    }

    deleteExp() {
        
        const { dispatch } = this.props;

        dispatch(deleteExperiment(this.state.expIdForCancel));
        
        return false;
    }


    dragEnd() {
        this.setState({update:true});
        //reset filter when splitter resize
        this.props.dispatch(this.props.dispatch(setFilter(null, null)));
    }


    closeDetails() {
        this.setState( {
            selectedExp: null
        });
    }

    sortHandler(col) {

        return () => {

            this.state.columns.map(c=>{
                c.active = false;
                return c;
            });

            let activeCol =_.find(this.state.columns, {name:col})
            activeCol.active = true;
            activeCol.sortOrder = activeCol.sortOrder === "asc" ? "desc" : "asc";
            
            this.setState({
                update: true
            })
        }
    }


    handleClose() {
        this.setState({
          dialogOpen:false
        });
    }

    handleDialogYesClick() {

        if (this.state.cb)
          this.state.cb();
    
        this.setState({dialogOpen:false});
    
      }

    render() {
        const { experiments, classes } = this.props; // eslint-disable-line no-unused-vars

        let sorted = [];

        let status, command, tags;
        
        if (this.props.experiments)  {
            let activeCol  =_.find(this.state.columns, {active:true});
            sorted = _.sortBy(this.props.experiments, (o) => {
                return o[activeCol.name];
            });
            if (activeCol.sortOrder === "desc") {
                _.reverse(sorted);
            }
        }

        if (this.state.selectedExp) {
            
            let index = _.findIndex(this.props.experiments, {experiment_id: this.state.selectedExp});
            let exps = this.props.experiments;

            if (index>=0) {
                status = JSON.stringify(exps[index].status);
                command =  ""; //exps[index].extra_details.command;
                tags = JSON.stringify( exps[index].tags);
            }
        }

        let splitterKey = this.splitterLayout ? this.splitterLayout.state.secondaryPaneSize : 0;

        return (
            <div className={classes.splitter} ref={(ref) => this.scrollParentRef = ref}>
                <SplitterLayout vertical="false" className={classes.splitter} percentage="true" secondaryInitialSize="60" onDragEnd={this.dragEnd} ref={(ref) => this.splitterLayout = ref}>
                    <Paper className={classes.root}>
                        <ExperimentChart key={splitterKey}/>
                    </Paper>
                    
                    <SplitterLayout vertical="false" percentage="true" secondaryInitialSize="50">

                        <Paper className={classes.root}>
                            <Table className={classes.table}>
                                <TableHead>
                                <TableRow>
                                        {
                                            this.state.columns.map(col=> {
                                                if (col.sortOrder === "")
                                                    return (
                                                        <TableCell align="right">
                                                            {col.title}
                                                        </TableCell>
                                                    )
                                                else 
                                                    return(
                                                        <TableCell align="right">
                                                            <TableSortLabel onClick={this.sortHandler(col.name)} active={col.active} direction={col.sortOrder}>{col.title}</TableSortLabel>                                        
                                                        </TableCell>
                                                )
                                            })
                                        }


                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {sorted && sorted.map(exp => {

                                        let disable = !(exp.status in ["in_progress", "created"]); // eslint-disable-line no-unused-vars

                                        return (

                                            <TableRow key={exp.experiment_id} onClick={this.rowClick} exp_id={exp.experiment_id} className={exp.experiment_id === this.state.selectedExp ? classes.highlight: null}>

                                                <TableCell align="right">{exp.experiment_id}</TableCell>
                                                <TableCell align="right">{exp.status}</TableCell>
                                                <TableCell align="right">
                                                    <a target="_blank" rel="noopener noreferrer" href={'http://' + window.location.hostname + ':5000' + exp.data_path}>
                                                    <FolderIcon className={classes.folder}/>
                                                    </a>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Button className={classes.cancel} color="secondary" exp_id={exp.experiment_id} disabled={disable} onClick={this.deleteClick(this.deleteExp)}>Delete</Button>

                                                </TableCell>
                                                <TableCell align="right">{formatDateString(exp.created)}</TableCell>
                                                <TableCell align="right">{formatDateString(exp.updated)}</TableCell>
                                            </TableRow>
                                        )}
                                    )}
                                </TableBody>
                            </Table>
                        </Paper>
                        { 
                            this.state.selectedExp &&
                            <Paper className={classes.details}>
                                <Card className = {classes.card}>
                                    <CardContent>
                                        
                                        <Grid container justify="space-between">
                                            <Grid item>
                                                <Typography variant="h5" className={classes.cardTitle}>Details</Typography>
                                            </Grid>
                                            <Grid item>
                                                <IconButton edge="start" onClick={this.closeDetails} className={classes.menuButton} color="inherit" aria-label="menu">
                                                    <ClearIcon className={classes.clearIcon}/>
                                                </IconButton>
                                            </Grid>
                                        </Grid>
                                        <Divider/>
                                        <List>
                                            <ListItem>
                                                <ListItemText className={classes.itemText}>Id:</ListItemText>
                                                <ListItemText className={classes.itemValue}>{this.state.selectedExp}</ListItemText>
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText className={classes.itemText}>Status</ListItemText>
                                                <ListItemText className={classes.itemValue}>{status}</ListItemText>
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText className={classes.itemText}>Command</ListItemText>
                                                <ListItemText className={classes.itemValue}>{command}</ListItemText>
                                            </ListItem>
                                            <ListItem>
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
                <Dialog
                    open={this.state.dialogOpen}
                    /*TransitionComponent={Transition}*/
                    keepMounted
                    onClose={this.handleClose}
                    aria-labelledby="dialogCoD"
                    aria-describedby="dialogCoDDesc"
                    >
                    <DialogTitle id="dialogCancel">Delete experiment</DialogTitle>
                    <DialogContent dividers>
                        <DialogContentText id="dialogCoDDesc">
                        Proceed to delete experiment '{this.state.expIdForCancel}'?
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={this.handleClose} color="default">
                        No
                        </Button>
                        <Button onClick={this.handleDialogYesClick} color="default">
                        Yes
                        </Button>
                    </DialogActions>
                </Dialog>
            </div>
        )
    }

}

function mapStateToProps(state) {
    
    return ({
        start: state.experiments.start,
        end: state.experiments.end,

        experiments: getExperimentsByFilter(state.experiments, state.start, state.end),      
    })

}

export default connect(mapStateToProps)(withStyles(styles, { withTheme: true })(ExperimentView));
