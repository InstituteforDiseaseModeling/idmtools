
import React from "react";
import { withStyles } from '@material-ui/core/styles';
import { connect } from "react-redux";
import { fetchSimulations, cancelSimulation } from "../../redux/action/simulation"
import { Table, TableHead, TableCell, TableSortLabel, TableRow, TableBody, Paper, Button, Typography, Divider,
        Card, CardContent, List, ListItem, ListItemText, Grid, IconButton,
        Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from "@material-ui/core";
import FolderIcon from "@material-ui/icons/Folder";
import ClearIcon from "@material-ui/icons/Clear";
import {formatDateString} from  "../../utils/utils";
import SplitterLayout from 'react-splitter-layout';
import SimulationChart from '../charts/simulationChart';
import * as _ from "lodash";
import {setFilter} from "../../redux/action/simulation";
import {getSimulationsByFilter} from "../../redux/selectors/simulations";

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
        height:'100%',  
    },
    root: {
        height:'100%',  
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
     },
     clearIcon: {
         color:'red',
         
     },
     tableHeader: {
         position:'sticky',
         top:200
     }
})

class SimulationView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            selectedSim : null,            
            columns: [
                {name: "simulation_uid", sortOrder:  'asc', active: false, title: 'Simulation Id' },
                {name: "status" , sortOrder:  'asc', active: false, title:'Status'},
                {name: "experiment_id" , sortOrder:  'asc', active: false, title: 'Experiment Id' },
                {name: "folder" , sortOrder:  '', active: false, title: 'Folder' },
                {name: "action" , sortOrder:  '', active: false, title: "Action" },
                {name: "created" , sortOrder:  'desc', active: true, title: "Created" },
                {name: "updated" , sortOrder:  'desc', active: false, title:"Updated" }
            ],
            dialogOpen: false,
            simIdForCancel: null
        }
        this.rowClick = this.rowClick.bind(this);
        this.cancelSim = this.cancelSim.bind(this);
        this.cancelClick = this.cancelClick.bind(this);
        this.dragEnd = this.dragEnd.bind(this);
        this.closeDetails = this.closeDetails.bind(this);
        this.sortHandler = this.sortHandler.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.handleDialogYesClick = this.handleDialogYesClick.bind(this);
    }

    componentDidMount() {
        const { dispatch } = this.props;

        dispatch(fetchSimulations());
    }

    cancelClick(cb) {
        return (e)=> {
            e.stopPropagation();
            e.preventDefault();

            this.setState({dialogOpen:true, cb: cb, simIdForCancel:e.currentTarget.getAttribute("sim_id") });

            return false;
          }      
    }

    cancelSim() {

        const { dispatch } = this.props;

        dispatch(cancelSimulation(this.state.simIdForCancel)); 
                
    }

    rowClick(e) {
        this.setState( {
            selectedSim : e.currentTarget.getAttribute("sim_id") == this.state.selectedSim ? null : e.currentTarget.getAttribute("sim_id")
        });
    }

    dragEnd() {

        this.setState({update:true})
        //reset filter when splitter resize
        this.props.dispatch(this.props.dispatch(setFilter(null, null)));
    }

    closeDetails() {
        this.setState( {
            selectedSim: null
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
            activeCol.sortOrder = activeCol.sortOrder == "asc" ? "desc" : "asc";
            
            this.setState({
                update: true
            })
        }
    }

    handleClose() {
        this.setState({
          dialogOpen:false
        })
    }

    handleDialogYesClick() {

        if (this.state.cb)
          this.state.cb();
    
        this.setState({dialogOpen:false});
    
      }
    

    render() {

        const { simulations , classes} = this.props;

        let sorted = [];

        let status, command, tags
        
        if (this.props.simulations) {

            let activeCol  =_.find(this.state.columns, {active:true});


            sorted = _.sortBy(this.props.simulations, (o) => {
                return o[activeCol.name];
            });

            if (activeCol.sortOrder == "desc") {
                _.reverse(sorted);
            }
        }


        if (this.state.selectedSim) {
            
            let index = _.findIndex(this.props.simulations, {simulation_uid: this.state.selectedSim});

            if (index >= 0) {
                let sims = this.props.simulations
                status = sims[index].status;
                command =  sims[index].extra_details.command;
                tags = JSON.stringify( sims[index].tags);                
            } else {
                this.state.selectedSim = null;
            }

        }

        let splitterKey = this.splitterLayout ? this.splitterLayout.state.secondaryPaneSize : 0;


        return (
            <div className={classes.splitter} ref={(ref) => this.scrollParentRef = ref}>
                <SplitterLayout vertical="false" className={classes.splitter} percentage="true" secondaryInitialSize="60" onDragEnd={this.dragEnd} ref={(ref) => this.splitterLayout = ref}>
                    <Paper className={classes.root}>
                        <SimulationChart key={splitterKey}/>
                    </Paper>
                    
                    <SplitterLayout vertical="false" percentage="true" secondaryInitialSize="50">
                    
                        <Paper className={classes.root}>
                            <Table className={classes.table}>
                                <TableHead className={classes.tableHeader}>
                                    <TableRow>
                                        {
                                            this.state.columns.map(col=> {
                                                if (col.sortOrder == "")
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
                                    {sorted.map(sim => {
                                        let disable = (sim.status == "done");

                                        debugger
                                        return (
                                            <TableRow key={sim.simulation_uid} onClick={this.rowClick} sim_id={sim.simulation_uid} className={sim.simulation_uid == this.state.selectedSim ? classes.highlight: null}>

                                                <TableCell align="right">{sim.simulation_uid}</TableCell>
                                                <TableCell align="right">{sim.status}</TableCell>
                                                <TableCell align="right">{sim.experiment_id}</TableCell>
                                                <TableCell align="right">
                                                    <a target="_blank" href={'http://' + window.location.hostname + ':5000' + sim.data_path}>
                                                        <IconButton edge="start" className={classes.menuButton} color="inherit" aria-label="menu">
                                                            <FolderIcon className={classes.folder}/>
                                                        </IconButton>
                                                    </a>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Button className={classes.cancel} color="secondary" disabled={disable} sim_id={sim.simulation_uid} onClick={this.cancelClick(this.cancelSim)}>Cancel</Button>

                                                </TableCell>
                                                <TableCell align="right">{formatDateString(sim.created)}</TableCell>
                                                <TableCell align="right">{formatDateString(sim.updated)}</TableCell>                                
                                            </TableRow>
                                    )})}
                                </TableBody>
                            </Table>
                        </Paper>
                        { this.state.selectedSim &&
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
                                                <ListItemText className={classes.itemValue}>{this.state.selectedSim}</ListItemText>
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
                <Dialog
                    open={this.state.dialogOpen}
                    /*TransitionComponent={Transition}*/
                    keepMounted
                    onClose={this.handleClose}
                    aria-labelledby="dialogCoD"
                    aria-describedby="dialogCoDDesc"
                    >
                    <DialogTitle id="dialogCancel">Cancel Simulation</DialogTitle>
                    <DialogContent dividers>
                        <DialogContentText id="dialogCoDDesc">
                        Proceed to cancel simulation '{this.state.simIdForCancel}'?
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
        start: state.start,
        end: state.end,
        simulations: getSimulationsByFilter(state.simulations, state.start, state.end),      
    })

}

export default connect(mapStateToProps)(withStyles(styles, { withTheme: true })(SimulationView));
