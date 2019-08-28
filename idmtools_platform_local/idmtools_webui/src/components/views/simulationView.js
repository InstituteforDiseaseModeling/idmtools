
import React from "react";
import { withStyles } from '@material-ui/core/styles';
import { connect } from "react-redux";
import { fetchSimulations, cancelSimulation } from "../../redux/action/simulation"
import { Table, TableHead, TableCell, TableRow, TableBody, Paper, Button, Typography, Divider,
        Card, CardContent, List, ListItem, ListItemText, TextField } from "@material-ui/core";
import FolderIcon from "@material-ui/icons/Folder";
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
     }
})

class SimulationView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            selectedSim : null
        }
        this.rowClick = this.rowClick.bind(this);
        this.cancelSim = this.cancelSim.bind(this);
        this.dragEnd = this.dragEnd.bind(this);
    }

    componentDidMount() {
        const { dispatch } = this.props;

        dispatch(fetchSimulations());
    }

    cancelSim(e) {
        e.stopPropagation();
        e.preventDefault();

        const { dispatch } = this.props;

        dispatch(cancelSimulation(e.currentTarget.getAttribute("sim_id")));
        
        return false;
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


    render() {

        const { simulations , classes} = this.props;

        let sorted = [];

        let status, command, tags
        
        if (this.props.simulations) 
            sorted = _.reverse(_.sortBy(this.props.simulations, (o) => {
                return o.created;
            }));

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
                            <TableHead>
                                <TableRow>
                                    
                                    <TableCell align="right">Simulation ID</TableCell>
                                    <TableCell align="right">Status</TableCell>
                                    <TableCell align="right">Experiment Id</TableCell>
                                    <TableCell align="right">Folder</TableCell>
                                    <TableCell align="center">Action</TableCell>
                                    <TableCell align="right">Created</TableCell>
                                    <TableCell align="right">Updated</TableCell>

                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {sorted.map(sim => (
                                    <TableRow key={sim.simulation_uid} onClick={this.rowClick} sim_id={sim.simulation_uid} className={sim.simulation_uid == this.state.selectedSim ? classes.highlight: null}>

                                        <TableCell align="right">{sim.simulation_uid}</TableCell>
                                        <TableCell align="right">{sim.status}</TableCell>
                                        <TableCell align="right">{sim.experiment_id}</TableCell>
                                        <TableCell align="right">
                                            <a target="_blank" href={'http://' + window.location.hostname + ':5000' + sim.data_path}>
                                            <FolderIcon className={classes.folder}/>
                                            </a>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Button className={classes.cancel} color="secondary" sim_id={sim.simulation_uid} onClick={this.cancelSim}>Cancel</Button>

                                        </TableCell>
                                        <TableCell align="right">{formatDateString(sim.created)}</TableCell>
                                        <TableCell align="right">{formatDateString(sim.updated)}</TableCell>                                
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Paper>
                    { this.state.selectedSim &&
                        <Paper className={classes.details}>
                            <Card className = {classes.card}>
                                <CardContent>
                                    
                                    <Typography variant="h5" className={classes.cardTitle}>Details</Typography>
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
