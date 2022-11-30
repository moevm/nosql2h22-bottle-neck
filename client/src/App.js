import './App.css';
import './index.css'
import * as React from 'react';
import ColorToggleButton from './components/toggle'
import InputComponent from "./components/inputComponent";
import {useEffect, useRef, useState} from "react";
function App(){

    const canvasRef = useRef(null);
    const contextRef = useRef(null);
    const [point1, point1State] = useState(null)
    const [point2, point2State] = useState(null)
    const [dataRoads, dataRoadsState] = useState(null)
    const [dataRoutes, dataRoutesState] = useState(null)
    const countCars = useRef(null);
    const radius = useRef(null);
    const isRadius = useRef(null);
    const [msg, msgState] = useState("")
    const typeRoads = useRef(null)
    const address =useRef(null)
    const minWorkload = useRef(null)
    const maxWorkload = useRef(null)
    const minLenght = useRef(null)
    const maxLenght = useRef(null)
    const minTime = useRef(null)
    const maxTime = useRef(null)
    useEffect(() => {
        const canvas = canvasRef.current;
        canvas.width = 830;
        canvas.height = 830;
        const context = canvas.getContext("2d");
        context.lineCap = "round";
        context.strokeStyle = "blue";
        context.lineWidth = 8;
        contextRef.current = context;
        let image_new = new Image()
        image_new.src = '/map_image'
        image_new.onload = function() {
            contextRef.current.drawImage(image_new, 0, 0, 830, 830)
        }
    }, []);
    const startDrawing = ({nativeEvent}) => {
        const {offsetX, offsetY} = nativeEvent;
        console.log(offsetX, offsetY)
        if(point1 === null){
            contextRef.current.beginPath();
            contextRef.current.moveTo(offsetX, offsetY);
            contextRef.current.lineTo(offsetX, offsetY);
            contextRef.current.stroke();
            point1State([offsetX, offsetY])
        }
        else if(point2 === null){
            contextRef.current.beginPath();
            contextRef.current.moveTo(offsetX, offsetY);
            contextRef.current.lineTo(offsetX, offsetY);
            contextRef.current.stroke();
            point2State([offsetX, offsetY])
        }
        console.log(point1, point2)
        nativeEvent.preventDefault();
    };
    function getPoints(){
        if(point2 != null && point1 != null){
            console.log(point1, point2);
            contextRef.current.beginPath();
            contextRef.current.moveTo(point1[0], point1[1]);
            contextRef.current.lineTo(point1[0], point1[1]);
            contextRef.current.stroke();
            contextRef.current.beginPath();
            contextRef.current.moveTo(point2[0], point2[1]);
            contextRef.current.lineTo(point2[0], point2[1]);
            contextRef.current.stroke();
        }
    }
    function getImage(flag = true){
        let image_new = new Image()
        image_new.src = '/map_image?' + new Date().getTime()
        image_new.onload = function() {
            contextRef.current.drawImage(image_new, 0, 0, 830, 830)
            if(flag){
                getPoints();
                console.log(flag, '2')
            }
        }
        console.log("img")
    }
    function dropPoints(){
        console.log(5)
        contextRef.current.globalCompositeOperation = 'destination-out';
        contextRef.current.lineWidth=10
        if(point1 != null){
            contextRef.current.lineTo(point1[0], point1[1]);
            contextRef.current.stroke()
            point1State(null)
        }
        if(point2 != null){
            contextRef.current.lineTo(point2[0], point2[1]);
            contextRef.current.stroke()
            point2State(null)
        }
        contextRef.current.lineWidth=8
        contextRef.current.globalCompositeOperation = 'source-over';
        getImage(false);
    }
    function getRoads(){
        fetch('/roads').then(response=>response.json())
            .then(json => dataRoadsState(json))
    }
    function getRoutes(){
        fetch('/routes').then(response=>response.json())
            .then(json => dataRoutesState(json))
    }
    //+ new URLSearchParams({
    //     foo: 'value',
    //     bar: 2,
    // })
    function filterRoads(ev){
        console.log(address.current.value)
        console.log(minWorkload.current.value)
        console.log(maxWorkload.current.value)
        console.log(typeRoads.current.value)
        if(minWorkload.current.value > maxWorkload.current.value){
            msgState("min загруженость > max загруженость")
        }
        else{
            msgState("")
            fetch('/roads?'+new URLSearchParams({
                min: minWorkload.current.value,
                max: maxWorkload.current.value,
                address: address.current.value,
                type: typeRoads.current.value
                 })).then(response=>response.json())
                .then(json => dataRoadsState(json))
        }
        ev.preventDefault();
    }
    function filterRoutes(ev){
        console.log(minLenght.current.value)
        console.log(maxLenght.current.value)
        console.log(minTime.current.value)
        console.log(maxTime.current.value)
        if(minLenght.current.value > maxLenght.current.value){
            msgState("min длина > max длины")
        }
        else if(minTime.current.value > maxTime.current.value){
            msgState("min время > max времени")
        }
        else{
            msgState("")
            fetch('/routes?'+new URLSearchParams({
                minTime: minTime.current.value,
                maxTime: maxTime.current.value,
                minLength: minLenght.current.value,
                maxLength: maxLenght.current.value
            })).then(response=>response.json())
                .then(json => dataRoutesState(json))
        }
        ev.preventDefault();
    }
    function simulate(ev){
        ev.preventDefault()
        console.log( point1[0], point1[1], point2[0], point2[1], radius.current.value,countCars.current.value)
        console.log('ee');
        console.log(point1 == null || point2 == null)
        if(point1 == null || point2 == null){
            msgState("Не указаны точки маршрута");
        }
        else{
            msgState("")
            console.log(2, 'radius.current.value',Number(radius.current.value)/1000)
            fetch("/simulate", {
                method: 'POST',
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "point1": {
                        "x": point1[0],
                        "y": point1[1]
                    },
                    "point2": {
                        "x": point2[0],
                        "y": point2[1]
                    },
                    "radius": Number(radius.current.value)/1000,
                    "car_count": countCars.current.value
                })
            }).then((responce)=>{
                console.log(responce);
                getImage();
                getPoints();
                getRoads();
                getRoutes();
            })
        }

    }
    function getCountRoutes(){
        if(dataRoutes == null){
            return (<p>Количество маршрутов: {0}</p>)
        }
        return (<p>Количество маршрутов: {dataRoutes.length}</p>)
    }
    return(
        <div className="App">
            <div className="right">
                <p>{msg}</p>
                <div className="inline">
                    <InputComponent value={0} label={"Количество машин"} type={"number"}
                                    onChange={() => console.log(1)} sRef={countCars}/>
                    <InputComponent value={false} label={"Радиус поиска маршрутов"} variant={"input"}
                                    type={"checkbox"} sRef={isRadius}/>

                </div>
                <input min={1} max={1000} step={1} type={"range"} name={"radius"} ref={radius}/>
                <div className="inline">
                    <button onClick={simulate}>Смоделировать</button>
                    <button onClick={(e)=>{
                        fetch("/clear", {
                            method: "DELETE"
                        }).then((response) =>{
                            dropPoints()
                            dataRoutesState(null);
                            dataRoadsState(null);
                        })
                        }}>Очистить точки на карте</button>
                </div>
                {getCountRoutes()}
                <br/>
                <ColorToggleButton typeRoads={typeRoads} address={address} minWorkload={minWorkload} maxWorkload={maxWorkload} minLenght={minLenght} maxLenght={maxLenght} minTime={minTime} maxTime={maxTime} filterRoads={filterRoads} filterRoutes={filterRoutes} dataRoads={dataRoads} dataRoutes={dataRoutes}/>
            </div>
            <div align="center">
                <div class="table">
                    <div class="row">
                        <div class="cell">
                            <canvas className="map"
                                    ref={canvasRef}
                                    onMouseDown={startDrawing}
                            >
                            </canvas>

                        </div>
                    </div>
                </div>
            </div>

        </div>
    )
}

export default App;
