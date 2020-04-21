
import React from "react";
import { withStyles } from '@material-ui/core/styles';
import { connect } from "react-redux";
import { fetchExperiments } from "../../redux/action/experiment"
import { fetchSimulations } from "../../redux/action/simulation"

import {Card, CardContent, Typography, Divider, List, ListItem, ListItemText, Paper}  from "@material-ui/core";


const styles = theme => ({
    card : {
        maxWidth: 400,
        width:200,
        margin:10,
        height:300,
        cursor:'pointer'
       
    },
    paper : {
        display:'flex',
        height:'100%'
    },
    cardTitle:{
        padding:10,
        color:'#6f9a37'  //green
    }
});

class Dashboard extends React.Component {

    handleCardClick(target) {
        return ()=> {      
            window.location.href = "/#/" + target;
          }      
    }


    componentDidMount() {
        const { dispatch } = this.props;
        dispatch(fetchSimulations());

        dispatch(fetchExperiments());
    }
    render() {
        const {classes, simulations, experiments} = this.props;

        
        let simStatus = { done:0, 'in progress':0, created:0 };

        let expCount = 0;

        if (simulations.simulations) {
            simulations.simulations.forEach((sim) => {
                simStatus[sim.status] += 1;
            })
        }

        if (experiments.experiments) {
            expCount = experiments.experiments.length;
            // experiments.experiments.map((exp)=> {
            //     expStatus["done"] += exp.progress[0].done ? exp.progress[0].done : 0;
            //     expStatus["in progress"] += exp.progress[0].inProgress ? exp.progress[0].inProgress : 0;
            //     expStatus["created"] += exp.progress[0].created ? exp.progress[0].created : 0;
            // })
        }


        return (
            <Paper className = {classes.paper}>
                <Card className = {classes.card} onClick={this.handleCardClick("experiment")}>
                    <CardContent>
                        
                        <Typography variant="h5" className={classes.cardTitle}>Local Experiments</Typography>
                        <Divider/>
                        <List>
                            <ListItem>
                                <ListItemText>Count:{expCount}</ListItemText>
                            </ListItem>
                        </List>
                    </CardContent>
                </Card>
                
                <Card className = {classes.card} onClick={this.handleCardClick("simulation")}>
                    <CardContent>                        
                        <Typography variant="h5" className={classes.cardTitle}>Local Simulations</Typography>
                        <Divider/>
                        
                        <List>
                            <ListItem>
                                <ListItemText>Done:{simStatus.done}</ListItemText>
                            </ListItem>
                            <ListItem>
                                <ListItemText>In progress:{simStatus['in progress']}</ListItemText>
                            </ListItem>
                            <ListItem>
                                <ListItemText>Created:{simStatus.created}</ListItemText>
                            </ListItem>
                        </List>
                        
                    </CardContent>
                </Card>
                {/* <Card className = {classes.card} onClick={this.handleCardClick("experiment")}>
                    <CardContent>
                        
                        <Typography variant="h5" className={classes.cardTitle}>COMPS Experiments</Typography>
                        <Divider/>
                        <List>
                            <ListItem>
                                <ListItemText>Completed:???</ListItemText>
                            </ListItem>
                            <ListItem>
                                <ListItemText>Running:</ListItemText>
                            </ListItem>

                        </List>
                    </CardContent>
                </Card>
                
                <Card className = {classes.card} onClick={this.handleCardClick("simulation")}>
                    <CardContent>
                        
                        <Typography variant="h5" className={classes.cardTitle}>COMPS Simulations</Typography>
                        <Divider/>
                        <List>
                            <ListItem>
                                <ListItemText>Completed:???</ListItemText>
                            </ListItem>
                            <ListItem>
                                <ListItemText>Running:</ListItemText>
                            </ListItem>
                        </List>
                    </CardContent>
                </Card> */}
                

            </Paper>
        )
    }

}

function mapStateToProps(state) {
    return ({
      simulations: state.simulations,
      experiments: state.experiments
    })
  
}

export default connect(mapStateToProps)(withStyles(styles, { withTheme: true })(Dashboard));
