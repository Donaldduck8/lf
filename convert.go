package main

import (
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"

	"github.com/markkurossi/tabulate"
)

func convertWeight(value float64, fromUnit string) {
	var g, kg, lbs, stone, ml, oz float64
	switch strings.ToLower(fromUnit) {
	case "g":
		g = value
		kg = value / 1000
		lbs = value / 453.592
		stone = value / 6350.29
		ml = value // assuming density of water
		oz = value / 28.3495
	case "kg":
		g = value * 1000
		kg = value
		lbs = value * 2.20462
		stone = value * 0.157473
		ml = value * 1000 // assuming density of water
		oz = value * 35.274
	case "lbs", "lb":
		g = value * 453.592
		kg = value * 0.453592
		lbs = value
		stone = value * 0.0714286
		ml = value * 453.592 // assuming density of water
		oz = value * 16.0
	case "stone":
		g = value * 6350.29
		kg = value * 6.35029
		lbs = value * 14
		stone = value
		ml = value * 6350.29 // assuming density of water
		oz = value * 224
	default:
		fmt.Println("Unknown unit")
		return
	}

	tab := tabulate.New(tabulate.Unicode)
	tab.Header("Unit").SetAlign(tabulate.MR)
	tab.Header("Value").SetAlign(tabulate.MR)

	row := tab.Row()
	row.Column("g")
	row.Column(fmt.Sprintf("%.2fg", g))

	row = tab.Row()
	row.Column("kg")
	row.Column(fmt.Sprintf("%.2fkg", kg))

	row = tab.Row()
	row.Column("lbs")
	row.Column(fmt.Sprintf("%.2flbs", lbs))

	row = tab.Row()
	row.Column("oz")
	row.Column(fmt.Sprintf("%.2foz", oz))

	row = tab.Row()
	row.Column("st")
	row.Column(fmt.Sprintf("%.2fst", stone))

	row = tab.Row()
	row.Column("ml")
	row.Column(fmt.Sprintf("%.2fml", ml))

	tab.Print(os.Stdout)
}

func convertTemperature(value float64, fromUnit string) {
	var c, f, k float64
	switch strings.ToLower(fromUnit) {
	case "c", "celsius":
		c = value
		f = value*9/5 + 32
		k = value + 273.15
	case "f", "fahrenheit":
		c = (value - 32) * 5 / 9
		f = value
		k = (value-32)*5/9 + 273.15
	case "k", "kelvin":
		c = value - 273.15
		f = (value-273.15)*9/5 + 32
		k = value
	default:
		fmt.Println("Unknown unit")
		return
	}

	tab := tabulate.New(tabulate.Unicode)
	tab.Header("Unit").SetAlign(tabulate.MR)
	tab.Header("Value").SetAlign(tabulate.MR)

	row := tab.Row()
	row.Column("Celsius")
	row.Column(fmt.Sprintf("%.2f°C", c))

	row = tab.Row()
	row.Column("Fahrenheit")
	row.Column(fmt.Sprintf("%.2f°F", f))

	row = tab.Row()
	row.Column("Kelvin")
	row.Column(fmt.Sprintf("%.2fK", k))

	tab.Print(os.Stdout)
}

func convertMethylphenidates(value float64, fromUnit string, fromUnitExtra string) {
	var c, f, k float64
	switch strings.ToLower(fromUnit) {
	case "c", "celsius":
		c = value
		f = value*9/5 + 32
		k = value + 273.15
	case "f", "fahrenheit":
		c = (value - 32) * 5 / 9
		f = value
		k = (value-32)*5/9 + 273.15
	case "k", "kelvin":
		c = value - 273.15
		f = (value-273.15)*9/5 + 32
		k = value
	default:
		fmt.Println("Unknown unit")
		return
	}

	tab := tabulate.New(tabulate.Unicode)
	tab.Header("Unit").SetAlign(tabulate.MR)
	tab.Header("Value").SetAlign(tabulate.MR)

	row := tab.Row()
	row.Column("Celsius")
	row.Column(fmt.Sprintf("%.2f°C", c))

	row = tab.Row()
	row.Column("Fahrenheit")
	row.Column(fmt.Sprintf("%.2f°F", f))

	row = tab.Row()
	row.Column("Kelvin")
	row.Column(fmt.Sprintf("%.2fK", k))

	tab.Print(os.Stdout)
}

func parseAndConvert(input string) {
	regexPattern := `([\d\.]+?)([a-zA-Z]+)\s*?(.*?)`
	regex := regexp.MustCompile(regexPattern)

	matches := regex.FindStringSubmatch(input)

	if len(matches) < 3 {
		fmt.Println("Invalid input format")
		return
	}

	value, err := strconv.ParseFloat(matches[1], 64)

	if err != nil {
		fmt.Println("Invalid input value format")
		return
	}

	unit := matches[2]
	unit = strings.ToLower(unit)

	extra := matches[3]

	switch unit {
	case "lb", "lbs", "kg", "g", "oz", "st":
		// This could be normal weight conversion, or a drug conversion
		if len(extra) == 0 {
			convertWeight(value, unit)
		}

		if len(extra) > 0 {
			// Drug conversion accepts one extra argument
			switch extra {
			case "ritalin", "concerta":
				//convertMethylphenidates(value, unit, extra)
			}
		}

	case "c", "f", "k":
		convertTemperature(value, unit)
	}

}
